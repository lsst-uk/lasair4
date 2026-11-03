"""Check that the main Lasair pages render against the seeded dev data.

Run from `dev/` with `make smoke` after `make seed`. Uses Django's test client
against the live local databases (it does not create a test database).
Exits non-zero if any page fails.
"""
import sys

from seed.guard import setup_dev_django

FAILED = 'FAIL'
# AN OBJECT THAT THE FRONT PAGE QUERY IN webserver/lasair/views.py:index MUST LIST
FRONT_PAGE_QUERY = ('SELECT o.objectId FROM objects o JOIN sherlock_classifications s ON o.objectId = s.objectId '
                    'WHERE o.jdmax > jdnow() - 7 AND (o.gmag < 17 OR o.rmag < 17) AND o.ncandgp > 1 '
                    'AND s.classification IN ("SN", "NT", "CV", "AGN") LIMIT 1')


def _first(cursor, query):
    cursor.execute(query)
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError('No seed data for: %s. Run `make seed` first.' % query)
    return row


def _targets(cursor):
    """Return (label, method, url, data, expectedText) for every page to check."""
    obj = _first(cursor, 'SELECT o.objectId FROM objects o JOIN watchlist_hits h ON o.objectId = h.objectId '
                         'WHERE h.wl_id = 1 LIMIT 1')
    objectId = obj['objectId']
    cand = _first(cursor, 'SELECT ramean, decmean FROM objects WHERE objectId = "%s"' % objectId)
    filterRow = _first(cursor, 'SELECT mq_id FROM myqueries WHERE name = "Recent supernova candidates"')
    watchlist = _first(cursor, 'SELECT wl_id FROM watchlists WHERE name = "Dev nearby galaxies"')
    watchmap = _first(cursor, 'SELECT ar_id FROM areas LIMIT 1')
    frontPage = _first(cursor, FRONT_PAGE_QUERY)
    cone = '%.5f %.5f' % (cand['ramean'], cand['decmean'])
    return [
        ('front page', 'get', '/', None, frontPage['objectId']),
        ('object page', 'get', '/objects/%s/' % objectId, None, objectId),
        ('search by name', 'get', '/search/%s' % objectId, None, objectId),
        ('search by cone', 'post', '/search/', {'query': cone}, objectId),
        ('filters list', 'get', '/filters/', None, 'Recent supernova candidates'),
        ('filter detail', 'get', '/filters/%d/' % filterRow['mq_id'], None, 'ZTF'),
        ('watchlists list', 'get', '/watchlists/', None, 'Dev nearby galaxies'),
        ('watchlist detail', 'get', '/watchlists/%d/' % watchlist['wl_id'], None, 'GAL-'),
        ('watchmaps list', 'get', '/watchmaps/', None, 'Dev sample area'),
        ('watchmap detail', 'get', '/watchmaps/%d/' % watchmap['ar_id'], None, 'ZTF'),
        ('annotators list', 'get', '/annotators/', None, 'dev_classifier'),
        ('annotator detail', 'get', '/annotators/dev_classifier/', None, 'dev_classifier'),
        ('schema', 'get', '/schema/', None, 'objectId'),
        ('status', 'get', '/status/', None, 'Night number'),
        ('API objects', 'get', '/api/objects/?objectIds=%s' % objectId, None, objectId),
        ('API lightcurves', 'get', '/api/lightcurves/?objectIds=%s' % objectId, None, 'magpsf'),
    ]


def _cutout_target(cursor):
    from lasair.utils import objjson
    objectId = _first(cursor, 'SELECT objectId FROM objects LIMIT 1')['objectId']
    data = objjson(objectId)
    cand = next(c for c in data['candidates'] if 'candid' in c)
    return ('cutout FITS', 'get', '/fits/%d/%d_cutoutScience/' % (cand['imjd'], cand['candid']), None, None)


def _check(client, apiHeaders, target):
    label, method, url, data, expected = target
    headers = apiHeaders if url.startswith('/api/') else {}
    response = getattr(client, method)(url, data, **headers) if data else getattr(client, method)(url, **headers)
    body = response.content.decode('utf-8', errors='replace') if expected else ''
    if response.status_code != 200:
        return FAILED, '%s %s -> HTTP %d' % (label, url, response.status_code)
    if expected and expected not in body:
        return FAILED, '%s %s -> missing %r' % (label, url, expected)
    if expected is None and not response.content.startswith(b'SIMPLE'):
        return FAILED, '%s %s -> not a FITS file' % (label, url)
    return 'ok', '%s %s' % (label, url)


def main():
    setup_dev_django()
    from django.contrib.auth.models import User
    from django.test import Client
    from rest_framework.authtoken.models import Token
    from src import db_connect

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    try:
        targets = _targets(cursor) + [_cutout_target(cursor)]
    finally:
        cursor.close()
        msl.close()

    user = User.objects.get(username='alice')
    client = Client(HTTP_HOST='127.0.0.1')
    client.force_login(user)
    apiHeaders = {'HTTP_AUTHORIZATION': 'Token %s' % Token.objects.get(user=user).key}

    failures = 0
    for target in targets:
        try:
            status, message = _check(client, apiHeaders, target)
        except Exception as exc:  # REPORT EVERY PAGE, EVEN IF ONE RAISES
            status, message = FAILED, '%s -> %s: %s' % (target[0], type(exc).__name__, exc)
        failures += status == FAILED
        print('%-4s %s' % (status, message))
    print('\n%d of %d checks passed' % (len(targets) - failures, len(targets)))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
