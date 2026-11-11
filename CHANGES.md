# Changes

## Unreleased

- **ENHANCEMENT**: `common/src/db_connect.py` reads optional `DB_DATABASE` and `LOCAL_DB_DATABASE` settings; the default stays `ztf`.
- **REFACTOR**: remove the unused Aladin Lite v2 files from `webserver/staticfiles/vendor/`.
- **FIXED**: every page stalled when the CDS servers were slow or down, because each page loaded Aladin Lite with a blocking script tag from the CDS website; Lasair now serves its own copy of Aladin Lite 3.8.1, loads it in the background on the home and object pages only, and shows a message in the sky map if it has not loaded after 10 seconds.
- **FIXED**: Add the missing `db_connect` import to the multimessenger map view.
- **FIXED**: Remove the unused `webserver/lasair/old_settings.py`, which held credentials.
