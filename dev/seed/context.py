"""Seed the user-facing records: users, watchlists, watchmaps, filters, annotators.

Pure helpers (`cone_hits`, `area_hits`) are tested on their own. The `seed_*`
functions need Django set up (see `seed.py`) and a MySQL cursor.
"""
import datetime
import json
import math
import os

import astropy.units as u
import numpy as np
from django.utils import timezone
from mocpy import MOC

from seed import paths

AREA_FITS = os.path.join(paths.REPO_ROOT, 'tests', 'system', 'sample_area.fits')
ARCSEC_PER_DEG = 3600.0
TNS_RADIUS_ARCSEC = 3.0
USER_WATCHLIST_RADIUS_ARCSEC = 5.0
N_TNS_OBJECTS = 15
N_WATCHLIST_OBJECTS = 20
N_WATCHLIST_DECOYS = 10
EXPIRY_DAYS = 180
TNS_TYPES = {'SN': ('SN', 'SN Ia'), 'NT': ('AT', 'TDE'), 'CV': ('AT', 'CV'), 'ORPHAN': ('AT', None)}
DEV_PASSWORDS = {'dev': 'dev', 'alice': 'alice'}


def _separation_arcsec(ra1, dec1, ra2, dec2):
    ra1, dec1, ra2, dec2 = map(math.radians, (ra1, dec1, ra2, dec2))
    cosSep = (math.sin(dec1) * math.sin(dec2) +
              math.cos(dec1) * math.cos(dec2) * math.cos(ra1 - ra2))
    return math.degrees(math.acos(max(-1.0, min(1.0, cosSep)))) * ARCSEC_PER_DEG


def cone_hits(objects, cones, radiusArcsec):
    """Return watchlist_hits rows for every object inside a cone."""
    hits = []
    for cone in cones:
        for obj in objects:
            arcsec = _separation_arcsec(obj['ramean'], obj['decmean'], cone['ra'], cone['decl'])
            if arcsec <= radiusArcsec:
                hits.append({'objectId': obj['objectId'], 'wl_id': cone['wl_id'],
                             'cone_id': cone['cone_id'], 'arcsec': arcsec, 'name': cone['name']})
    return hits


def area_hits(objects, mocPath):
    """Return the objectIds that fall inside the MOC in `mocPath`."""
    if not objects:
        return []
    moc = MOC.from_fits(mocPath)
    ras = np.array([o['ramean'] for o in objects]) * u.deg
    decs = np.array([o['decmean'] for o in objects]) * u.deg
    inside = moc.contains_lonlat(ras, decs)
    return [o['objectId'] for o, isInside in zip(objects, inside) if isInside]


# ---------------------------------------------------------------------------
# SEEDING (NEEDS DJANGO SET UP)
# ---------------------------------------------------------------------------

def seed_users():
    """Create the dev superuser and a normal user, each with an API token."""
    from django.contrib.auth.models import User
    from rest_framework.authtoken.models import Token

    users = {}
    for username, first, last, isAdmin in (('dev', 'Dev', 'Admin', True), ('alice', 'Alice', 'Astronomer', False)):
        user, _ = User.objects.get_or_create(username=username, defaults={
            'first_name': first, 'last_name': last, 'email': '%s@lasair-dev.local' % username,
            'is_staff': isAdmin, 'is_superuser': isAdmin})
        user.set_password(DEV_PASSWORDS[username])
        user.save()
        Token.objects.get_or_create(user=user)
        users[username] = user
    return users


def _insert_hits(cursor, hits):
    cursor.executemany(
        'REPLACE INTO watchlist_hits (objectId, wl_id, cone_id, arcsec, name) VALUES (%s, %s, %s, %s, %s)',
        [(h['objectId'], h['wl_id'], h['cone_id'], h['arcsec'], h['name']) for h in hits])


def _make_cones(watchlist, entries):
    from lasair.apps.watchlist.models import WatchlistCone

    cones = []
    for name, ra, dec in entries:
        cone = WatchlistCone.objects.create(wl=watchlist, name=name, ra=ra, decl=dec)
        cones.append({'cone_id': cone.cone_id, 'wl_id': watchlist.wl_id, 'name': name, 'ra': ra, 'decl': dec})
    return cones


def _tns_row(alert, obj, index, nowUtc):
    prefix, tnsType = TNS_TYPES.get(alert['lasair_dev']['type'], ('AT', None))
    discovered = nowUtc - datetime.timedelta(days=float(obj['age']))
    name = '%d%s' % (nowUtc.year, ''.join(chr(97 + (index // 26 ** p) % 26) for p in (2, 1, 0)))
    return {'ra': obj['ramean'], 'decl': obj['decmean'], 'tns_name': name, 'tns_prefix': prefix,
            'disc_mag': round(alert['candidate']['magpsf'], 2), 'disc_mag_filter': 'r-ZTF',
            'type': tnsType, 'z': 0.05 if tnsType else None, 'hostz': None, 'host_name': None,
            'ext_catalogs': None, 'disc_int_name': alert['objectId'], 'disc_date': discovered,
            'lastmodified_date': nowUtc, 'sender': 'ZTF_Bot1', 'reporters': 'Lasair dev seed',
            'source_group': 'ZTF', 'htm16': obj['htm16'], 'lasairmodified_date': nowUtc}


def seed_tns(cursor, owner, tnsWatchlistId, alerts, objects):
    """Create the __TNS__ watchlist, crossmatch_tns rows and their hits."""
    from lasair.apps.watchlist.models import Watchlist

    watchlist = Watchlist.objects.create(wl_id=tnsWatchlistId, user=owner, name='__TNS__',
                                         description='Copy of Transient Name Server (dev seed)',
                                         active=True, public=False, radius=TNS_RADIUS_ARCSEC)
    alertById = {a['objectId']: a for a in alerts}
    chosen = [o for o in objects if alertById.get(o['objectId'], {}).get('lasair_dev', {}).get('type') in TNS_TYPES]
    nowUtc = datetime.datetime.utcnow().replace(microsecond=0)
    rows = [_tns_row(alertById[o['objectId']], o, i, nowUtc) for i, o in enumerate(chosen[:N_TNS_OBJECTS])]
    if not rows:
        return 0
    columns = list(rows[0])
    cursor.executemany(
        'INSERT INTO crossmatch_tns (%s) VALUES (%s)' % (', '.join(columns), ', '.join(['%s'] * len(columns))),
        [tuple(r[c] for c in columns) for r in rows])
    cones = _make_cones(watchlist, [(r['tns_name'], r['ra'], r['decl']) for r in rows])
    _insert_hits(cursor, cone_hits(objects, cones, TNS_RADIUS_ARCSEC))
    return len(rows)


def seed_user_watchlist(cursor, owner, objects, rng):
    """Create a public watchlist with cones on some objects plus some decoys."""
    from lasair.apps.watchlist.models import Watchlist

    expire = timezone.now() + datetime.timedelta(days=EXPIRY_DAYS)
    watchlist = Watchlist.objects.create(user=owner, name='Dev nearby galaxies',
                                         description='Synthetic watchlist from the dev seed',
                                         active=True, public=True, radius=USER_WATCHLIST_RADIUS_ARCSEC,
                                         date_expire=expire)
    picks = objects[1:1 + 2 * N_WATCHLIST_OBJECTS:2]
    entries = [('GAL-%03d' % i, o['ramean'] + 1.0 / ARCSEC_PER_DEG, o['decmean']) for i, o in enumerate(picks)]
    entries += [('DECOY-%03d' % i, rng.uniform(0, 360), rng.uniform(-30, 80)) for i in range(N_WATCHLIST_DECOYS)]
    cones = _make_cones(watchlist, entries)
    hits = cone_hits(objects, cones, USER_WATCHLIST_RADIUS_ARCSEC)
    _insert_hits(cursor, hits)
    return watchlist, len(hits)


def seed_watchmap(cursor, owner, objects):
    """Create a public watchmap from the repo's sample MOC and its area hits."""
    from lasair.apps.watchmap.models import Watchmap
    from lasair.apps.watchmap.utils import make_image_of_MOC
    from lasair.utils import bytes2string

    with open(AREA_FITS, 'rb') as mocFile:
        mocBytes = mocFile.read()
    watchmap = Watchmap.objects.create(
        user=owner, name='Dev sample area', description='Sample MOC from tests/system/sample_area.fits',
        moc=bytes2string(mocBytes), mocimage=bytes2string(make_image_of_MOC(mocBytes, request=None)),
        active=True, public=True, date_expire=timezone.now() + datetime.timedelta(days=EXPIRY_DAYS))
    hits = area_hits(objects, AREA_FITS)
    cursor.executemany('REPLACE INTO area_hits (objectId, ar_id) VALUES (%s, %s)',
                       [(objectId, watchmap.ar_id) for objectId in hits])
    return watchmap, len(hits)


def _filter_specs(watchlistId, watchmapId):
    return [
        ('Lightweight', 'Every object (heartbeat query)', 'objects.objectId', 'objects', ''),
        ('Recent supernova candidates', 'Sherlock SN, detected in the last 14 days',
         'objects.objectId, objects.gmag, objects.rmag, jdnow()-objects.jdmax AS age, '
         'sherlock_classifications.classification',
         'objects, sherlock_classifications',
         "sherlock_classifications.classification = 'SN' AND objects.jdmax > jdnow() - 14"),
        ('Bright and rising', 'Brighter than 18.5 and rising in g',
         'objects.objectId, objects.gmag, objects.dmdt_g', 'objects',
         'objects.gmag < 18.5 AND objects.dmdt_g < 0'),
        ('Watchlist matches', 'Objects in the dev watchlist',
         'objects.objectId, watchlist_hits.name, watchlist_hits.arcsec',
         'objects, watchlist:%d' % watchlistId, ''),
        ('In the sample area', 'Objects inside the dev watchmap',
         'objects.objectId, objects.ramean, objects.decmean', 'objects, area:%d' % watchmapId, ''),
    ]


def seed_filters(owner, watchlistId, watchmapId):
    """Create saved filters. None are active, so nothing tries to reach Kafka."""
    from lasair.apps.filter_query.models import filter_query
    from query_builder import build_query, check_query

    created = []
    for name, description, selected, tables, conditions in _filter_specs(watchlistId, watchmapId):
        error = check_query(selected, tables, conditions)
        if error:
            raise ValueError('Seed filter %r is invalid: %s' % (name, error))
        topic = 'lasair_%d%s' % (owner.id, ''.join(c for c in name if c.isalnum()))
        created.append(filter_query.objects.create(
            user=owner, name=name, description=description, selected=selected, tables=tables,
            conditions=conditions, public=True, active=0, topic_name=topic,
            real_sql=build_query(selected, tables, conditions)))
    return created


def seed_annotator(cursor, owner, objects):
    """Create a public annotator and one annotation per object."""
    from lasair.apps.annotator.models import Annotators

    topic = 'dev_classifier'
    Annotators.objects.create(topic=topic, description='Synthetic classifier from the dev seed',
                              user=owner, username=owner.username, url='https://lasair.readthedocs.io',
                              active=1, public=1)
    rows = []
    for obj in objects:
        ncand = obj['ncand'] or 0
        label = 'short' if ncand < 10 else 'medium' if ncand < 40 else 'long'
        rows.append((obj['objectId'], topic, '0.1', label, 'ncand is %d' % ncand,
                     json.dumps({'ncand': ncand}), None))
    cursor.executemany(
        'REPLACE INTO annotations (objectId, topic, version, timestamp, classification, explanation, classdict, url) '
        'VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s)', rows)
    return len(rows)


def write_status_files(systemStatusPrefix, nid, nObjects):
    """Write status JSON for today and yesterday, read by the status page."""
    os.makedirs(os.path.dirname(systemStatusPrefix), exist_ok=True)
    for offset in (0, 1):
        status = {'today_alert': 1200 - 100 * offset, 'today_candidate': 900, 'today_filter': 800,
                  'today_filter_out': 650, 'today_filter_ss': 120, 'today_ztf': 1250,
                  'today_database': 640, 'total_count': nObjects, 'min_delay': 0.5,
                  'nid': nid - offset, 'mjd': nid - offset + 57754, 'countTNS': N_TNS_OBJECTS,
                  'update_time': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
        with open('%s_%d.json' % (systemStatusPrefix, nid - offset), 'w') as statusFile:
            json.dump(status, statusFile, indent=2)
