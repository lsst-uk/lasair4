# Lasair local development stack

This folder holds a local development stack for the Lasair-ZTF web app. It lets you run the Django site on a Mac with fake data, without access to the live alert stream.

## Contents

- [Prerequisites](#prerequisites)
- [Set up the stack](#set-up-the-stack)
- [Make targets](#make-targets)
- [Fake data](#fake-data)
- [Generated files](#generated-files)
- [Known limitations](#known-limitations)
- [Safety checks](#safety-checks)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Install these before you start.

- macOS with [Homebrew](https://brew.sh).
- Python 3.11: `brew install python@3.11`. The Makefile looks for it at `/opt/homebrew/opt/python@3.11/bin/python3.11`. If your copy is elsewhere, set `PYTHON_BIN` (for example `make all PYTHON_BIN=/path/to/python3.11`).
- MariaDB from Homebrew. It must run on `127.0.0.1:3306`, and you must have an admin login (for example `root`).
- colima and the Docker command-line tool: `brew install colima docker`. The stack uses them to run Cassandra in a container. You do not need `docker compose`.

Run all `make` and `mysql` commands in this folder (`dev/`).

## Set up the stack

1. Create the database, the database users, and the `jdnow()` SQL function. You do this once.

   ```bash
   mysql -u root -p < db/bootstrap.sql
   ```

   The script creates:

   - the database `lasair_dev` (character set `utf8mb3`, collation `utf8mb3_unicode_ci`)
   - the users `lasair_dev_rw` and `lasair_dev_ro`. Each password is the same as the user name. The users can connect only from the local computer (`localhost` and `127.0.0.1`).
   - the SQL function `jdnow()`

   The script fails on purpose if `lasair_dev` already exists. It never touches an existing `ztf` database.

2. Build everything.

   ```bash
   make all
   ```

   This runs these targets in order: `venv`, `settings`, `cassandra-up`, `db`, `migrate`, `seed`. The first run takes several minutes because it installs packages and downloads the Cassandra image.

3. Start the web server.

   ```bash
   make run
   ```

4. Open <http://127.0.0.1:8080/> in a browser. To use a different port, run `make run PORT=8090`.

5. Log in with one of these accounts:

   | User | Password | Role |
   | --- | --- | --- |
   | `dev` | `dev` | superuser |
   | `alice` | `alice` | regular user |

6. Optional: check that the main pages work.

   ```bash
   make smoke
   ```

## Make targets

| Target | What it does |
| --- | --- |
| `all` | Runs `venv`, `settings`, `cassandra-up`, `db`, `migrate`, and `seed`. |
| `venv` | Creates `.venv` and installs `requirements-dev.txt`. |
| `settings` | Copies `settings.dev.py` to `webserver/lasair/settings.py`. See the note below. |
| `cassandra-up` | Starts colima if needed, starts the Cassandra container `lasair-dev-cassandra`, and creates the schema. |
| `cassandra-down` | Stops the Cassandra container. |
| `cassandra-schema` | Applies `cassandra/schema.cql` to the running container. |
| `db` | Creates the MySQL tables in `lasair_dev` from `common/schema`. |
| `migrate` | Generates dev-only migrations and runs the Django migrations. |
| `seed` | Reloads the fake data. It runs `seed.seed --reset`. |
| `run` | Starts the Django development server on `127.0.0.1:$(PORT)`. |
| `smoke` | Checks 17 pages and API routes against the seeded data. It exits with an error if one fails. |
| `test` | Runs the unit tests for the seed code. |
| `reset` | Deletes everything and rebuilds it. See the warning below. |

The `settings` target creates the secret key in `var/secret_key` if it does not exist. If `webserver/lasair/settings.py` already exists and is not a copy of the dev settings, the target first moves it to `settings.py.bak-<timestamp>`. Git ignores these backup files.

**Warning:** `make reset` drops every table in the `lasair_dev` database and drops the Cassandra keyspace `lasair`. It then rebuilds both. You lose all data in them, including changes you made in the web app. It does not touch other databases.

## Fake data

`make seed` deletes the earlier seed data and loads new data. The data includes:

- About 200 synthetic objects of types `SN`, `NT`, `AGN`, `VS`, `CV`, `BS`, `ORPHAN`, and `SS`. The seed also loads the sample alerts from the repository, with their dates moved to recent dates. With the default settings the total is 208 objects.
- Lightcurves and forced photometry in Cassandra.
- Science, Template, and Difference FITS cutouts.
- Sherlock classifications.
- 15 TNS matches, which you see through the `__TNS__` watchlist.
- A user watchlist, "Dev nearby galaxies".
- A watchmap, "Dev sample area", built from `tests/system/sample_area.fits`.
- 5 inactive public filters.
- The annotator `dev_classifier`.

The data is deterministic. The same options always give the same data. To change the options, run the seed command yourself:

```bash
LASAIR_DEV_STACK=1 .venv/bin/python -m seed.seed --reset --n-objects 200
```

The dev settings load only when the environment variable `LASAIR_DEV_STACK` is `1`. The Makefile sets it for every target. Set it yourself when you run a command outside `make`, for example `manage.py shell`.

| Option | Default | Meaning |
| --- | --- | --- |
| `--reset` | off | Delete existing seed data first. |
| `--n-objects` | `200` | Number of synthetic objects. |
| `--seed` | `20171` | Random seed. |

## Generated files

The stack writes its state to `var/`. Git ignores this folder. It holds:

- the FITS cutouts
- the status files
- the secret key
- the front page cache
- dev-only migrations for the `watchlist`, `watchmap`, and `filter_query` apps

These three apps have no migrations in Git. `MIGRATION_MODULES` in the dev settings points to `var/dev_migrations`, so the stack does not change the migration history of the repository.

The dev settings also set `DB_DATABASE` and `LOCAL_DB_DATABASE` to `lasair_dev`. `common/src/db_connect.py` reads these optional settings. When they are missing, it uses the database `ztf`.

## Known limitations

- The multimessenger map does not work. It needs skymap files and database tables that the dev stack does not create.
- You cannot save an active filter. This needs Kafka, which the dev stack does not run. Inactive filters work.
- The Aladin context map and some other parts of pages load data from external sites. They need an internet connection.

## Safety checks

The stack has checks that stop it from changing anything other than the local dev stack:

- `dev/settings.dev.py` refuses to load unless `LASAIR_DEV_STACK=1`. A web server that does not set this variable cannot use the dev settings.
- Before `db`, `migrate`, `seed`, `run`, `smoke`, and `reset`, the Makefile runs `python -m seed.guard`. The guard stops the target unless the active settings come from `webserver/lasair/settings.py`, use the database `lasair_dev` as the user `lasair_dev_rw` on port 3306, use only local hosts for MariaDB and Cassandra, and keep the generated migrations in `var/dev_migrations`. It also stops if `DJANGO_SETTINGS_MODULE` names other settings. `seed` and `smoke` run the same check in Python.
- The database and container names in the Makefile cannot be overridden on the command line.
- The Makefile creates the Cassandra container with the label `lasair-dev-stack=1`. The Cassandra targets refuse to use a container called `lasair-dev-cassandra` that does not have this label.

## Troubleshooting

**A Cassandra target says the container was not made by `dev/Makefile`.** A container called `lasair-dev-cassandra` exists without the dev label, for example from an earlier version of the stack. If it is yours and holds nothing you need, remove it with `docker rm -f lasair-dev-cassandra`, then run `make cassandra-up`.

**A command fails with "These are the local dev settings".** You ran it outside `make` without `LASAIR_DEV_STACK=1`. Add the variable to the command.

**Cassandra does not start.** Start colima with more resources, then run the target again:

```bash
colima start --cpu 2 --memory 4
make cassandra-up
```

**The front page shows old data after you change the database.** The front page caches its query for 60 seconds (`FRONT_PAGE_STALE`) in `var/front_page_cache.json`. Wait 60 seconds, or run `make seed`, which deletes the cache file.

**`bootstrap.sql` fails because `lasair_dev` exists.** This is on purpose. If you want to start again, drop the database yourself (`DROP DATABASE lasair_dev;`) and run the script again. Check first that the database holds nothing you need.
