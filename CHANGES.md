# Changes

## Unreleased

- **ENHANCEMENT**: `common/src/db_connect.py` reads optional `DB_DATABASE` and `LOCAL_DB_DATABASE` settings; the default stays `ztf`.
- **FIXED**: Add the missing `db_connect` import to the multimessenger map view.
- **FIXED**: Remove the unused `webserver/lasair/old_settings.py`, which held credentials.
