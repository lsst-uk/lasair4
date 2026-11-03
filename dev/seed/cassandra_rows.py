"""Turn alerts into Cassandra rows and load them.

The split mirrors `insert_cassandra()` in `pipeline/ingest/ingest.py`, so the
webserver reads data shaped exactly as production ingest writes it.
"""
from cassandra.concurrent import execute_concurrent_with_args
from gkhtm import _gkhtm as htmCircle

NON_DETECTION_COLUMNS = ('jd', 'fid', 'diffmaglim', 'nid', 'field',
                         'magzpsci', 'magzpsciunc', 'magzpscirms')
HTM_LEVEL = 16
CONCURRENCY = 50


def _lowercase(row):
    return {key.lower(): value for key, value in row.items()}


def split_alert(alert):
    """Return (candidates, noncandidates, forcedphot) row lists for one alert."""
    objectId = alert['objectId']
    history = list(alert.get('prv_candidates') or []) + [alert['candidate']]

    detections, nonDetections = [], []
    for cand in history:
        if cand.get('candid'):
            row = _lowercase(cand)
            row['objectid'] = objectId
            detections.append(row)
        else:
            row = {key: cand.get(key) for key in NON_DETECTION_COLUMNS}
            row['objectid'] = objectId
            nonDetections.append(row)

    if detections:
        htmIds = htmCircle.htmIDBulk(HTM_LEVEL, [[row['ra'], row['dec']] for row in detections])
        for row, htmId in zip(detections, htmIds):
            row['htmid16'] = htmId

    forced = []
    for fp in alert.get('fp_hists') or []:
        row = _lowercase(fp)
        row['objectid'] = objectId
        forced.append(row)
    return detections, nonDetections, forced


def insert_rows(session, table, rows, allowedColumns):
    """Insert dict rows into `table`, keeping only columns the table has."""
    statements = {}
    groups = {}
    for row in rows:
        columns = tuple(sorted(k for k in row if k in allowedColumns))
        groups.setdefault(columns, []).append(tuple(row[c] for c in columns))
    for columns, values in groups.items():
        if columns not in statements:
            cql = 'INSERT INTO %s (%s) VALUES (%s)' % (table, ', '.join(columns), ', '.join('?' * len(columns)))
            statements[columns] = session.prepare(cql)
        results = execute_concurrent_with_args(session, statements[columns], values,
                                               concurrency=CONCURRENCY, raise_on_first_error=True)
        for success, result in results:
            if not success:
                raise RuntimeError('Cassandra insert into %s failed: %s' % (table, result))


def table_columns(session, keyspace, table):
    """Return the set of column names Cassandra has for `table`."""
    rows = session.execute(
        'SELECT column_name FROM system_schema.columns WHERE keyspace_name=%s AND table_name=%s',
        (keyspace, table))
    return {row['column_name'] if isinstance(row, dict) else row.column_name for row in rows}
