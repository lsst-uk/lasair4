"""Load fake data into the local Lasair dev stack.

Run from `dev/` with `make seed`, or directly:

    .venv/bin/python -m seed.seed --reset --n-objects 200
"""
import argparse
import contextlib
import logging
import os
import sys

import numpy as np

from seed.guard import setup_dev_django

DEFAULT_SEED = 20171
DEFAULT_N_OBJECTS = 200
MYSQL_TABLES = ('objects', 'sherlock_classifications', 'watchlist_hits', 'area_hits',
                'crossmatch_tns', 'annotations')
DJANGO_TABLES = ('myqueries', 'areas', 'watchlist_cones', 'watchlists', 'annotators')
CASSANDRA_TABLES = ('candidates', 'noncandidates', 'forcedphot')
MJD_OFFSET = 2400000.5

log = logging.getLogger('lasair-dev-seed')


def _reset(msl, cursor, cassandraSession):
    log.info('Removing existing seed data')
    cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
    for table in MYSQL_TABLES + DJANGO_TABLES:
        cursor.execute('DELETE FROM %s' % table)
    cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
    # COMMIT FIRST: DJANGO USES ITS OWN CONNECTION AND WOULD WAIT ON THESE ROW LOCKS
    msl.commit()
    from django.contrib.auth.models import User
    User.objects.filter(username__in=('dev', 'alice')).delete()
    for table in CASSANDRA_TABLES:
        cassandraSession.execute('TRUNCATE %s' % table)


def _load_alerts(cursor, cassandraSession, store, alerts):
    from seed.cassandra_rows import insert_rows, split_alert, table_columns
    from seed.cutouts import write_cutouts
    from seed.mysql_rows import make_sherlock, object_query, sherlock_query

    columns = {t: table_columns(cassandraSession, 'lasair', t) for t in CASSANDRA_TABLES}
    rows = {t: [] for t in CASSANDRA_TABLES}
    nCutouts = 0
    for index, alert in enumerate(alerts):
        query = object_query(alert)
        if query is None:
            log.warning('No objects row for %s, skipped', alert['objectId'])
            continue
        cursor.execute(query)
        cursor.execute(sherlock_query(alert['objectId'], make_sherlock(alert)))
        cands, nonCands, forced = split_alert(alert)
        rows['candidates'] += cands
        rows['noncandidates'] += nonCands
        rows['forcedphot'] += forced
        for cand in cands:
            imjd = int(cand['jd'] - MJD_OFFSET)
            write_cutouts(store, cand['candid'], imjd, seed=index, negative=cand.get('isdiffpos') == 'f')
            nCutouts += 3
    for table, tableRows in rows.items():
        insert_rows(cassandraSession, table, tableRows, columns[table])
        log.info('Cassandra %s: %d rows', table, len(tableRows))
    log.info('Cutout FITS files: %d', nCutouts)


def _object_summaries(cursor):
    cursor.execute('SELECT objectId, ramean, decmean, ncand, htm16, jdnow() - jdmax AS age FROM objects')
    return cursor.fetchall()


def _seed_context(cursor, settings, alerts, seed):
    """Add users, TNS matches, a watchlist, a watchmap, filters and annotations around the objects."""
    from seed import context

    objects = _object_summaries(cursor)
    log.info('MySQL objects: %d', len(objects))
    users = context.seed_users()
    nTns = context.seed_tns(cursor, users['dev'], settings.TNS_WATCHLIST_ID, alerts, objects)
    rng = np.random.default_rng(seed)
    watchlist, nWatchlistHits = context.seed_user_watchlist(cursor, users['alice'], objects, rng)
    watchmap, nAreaHits = context.seed_watchmap(cursor, users['alice'], objects)
    filters = context.seed_filters(users['alice'], watchlist.wl_id, watchmap.ar_id)
    nAnnotations = context.seed_annotator(cursor, users['alice'], objects)
    log.info('TNS: %d, watchlist hits: %d, area hits: %d, filters: %d, annotations: %d',
             nTns, nWatchlistHits, nAreaHits, len(filters), nAnnotations)


def run(seed, nObjects, reset):
    settings = setup_dev_django()
    from cassandra.cluster import Cluster
    from cassandra.query import dict_factory
    from objectStore import objectStore
    from src import db_connect

    from seed import context
    from seed.alerts import SAMPLE_ALERT_DIR, jd_now, load_sample_alerts, make_alerts, nid_for_jd

    with contextlib.ExitStack() as cleanup:
        msl = db_connect.remote()
        cleanup.callback(msl.close)
        cursor = msl.cursor(buffered=True, dictionary=True)
        cleanup.callback(cursor.close)
        cluster = Cluster(settings.CASSANDRA_HEAD)
        cleanup.callback(cluster.shutdown)
        cassandraSession = cluster.connect('lasair')
        cassandraSession.row_factory = dict_factory
        cursor.execute('SELECT COUNT(*) AS n FROM objects')
        if cursor.fetchone()['n'] and not reset:
            log.error('The objects table already has data. Use --reset to replace it.')
            return 1
        if reset:
            _reset(msl, cursor, cassandraSession)

        nowJd = jd_now()
        alerts = make_alerts(seed=seed, nObjects=nObjects, nowJd=nowJd)
        alerts += load_sample_alerts(SAMPLE_ALERT_DIR, nowJd=nowJd)
        store = objectStore(suffix='fits', fileroot=settings.IMAGEFITS)
        _load_alerts(cursor, cassandraSession, store, alerts)
        msl.commit()

        _seed_context(cursor, settings, alerts, seed)
        msl.commit()
        context.write_status_files(settings.SYSTEM_STATUS, nid_for_jd(nowJd), len(_object_summaries(cursor)))
        # THE FRONT PAGE CACHES ITS QUERY RESULT; REMOVE THE CACHE SO IT SHOWS THE NEW DATA
        if os.path.exists(settings.FRONT_PAGE_CACHE):
            os.remove(settings.FRONT_PAGE_CACHE)
        log.info('Done. Log in at http://127.0.0.1:8080/ as dev/dev or alice/alice.')
        return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--reset', action='store_true', help='delete existing seed data first')
    parser.add_argument('--n-objects', type=int, default=DEFAULT_N_OBJECTS, help='synthetic objects to make')
    parser.add_argument('--seed', type=int, default=DEFAULT_SEED, help='random seed')
    args = parser.parse_args(argv)
    if args.n_objects < 1:
        parser.error('--n-objects must be at least 1')
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    return run(args.seed, args.n_objects, args.reset)


if __name__ == '__main__':
    sys.exit(main())
