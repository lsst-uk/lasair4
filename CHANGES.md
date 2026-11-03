# Changes

## Unreleased

- **FEATURE**: Add a local development stack in `dev/` (MariaDB, Cassandra container, seeded fake data, smoke test) to run the Django web app on macOS.
- **ENHANCEMENT**: `common/src/db_connect.py` reads optional `DB_DATABASE` and `LOCAL_DB_DATABASE` settings; the default stays `ztf`.
- **FIXED**: Add the missing `db_connect` import to the multimessenger map view.
