"""Refuse to run dev tools unless the dev settings are active.

`make seed` deletes data and `make migrate` writes migrations, so both must
only ever run against the local dev stack. Run `python -m seed.guard` from
`dev/` to check the settings that `import settings` would load.
"""
import os
import sys

from seed import paths

DEV_DATABASE = 'lasair_dev'
DEV_DB_USER = 'lasair_dev_rw'
DEV_DB_USER_READONLY = 'lasair_dev_ro'
DEV_DB_PORT = 3306
LOOPBACK_HOSTS = ('127.0.0.1', 'localhost', '::1')
DEV_MIGRATIONS_PACKAGE = 'dev_migrations.'
# THE APPS WITH NO MIGRATIONS IN GIT; KEEP IN STEP WITH DJANGO_APPS_WITHOUT_MIGRATIONS IN dev/Makefile
APPS_WITH_DEV_MIGRATIONS = ('watchlist', 'watchmap', 'filter_query')
DEV_SETTINGS_FILE = os.path.join(paths.WEBSERVER_ROOT, 'lasair', 'settings.py')
DJANGO_SETTINGS_NAME = 'settings'


def _default_database(settings):
    databases = getattr(settings, 'DATABASES', None)
    default = databases.get('default') if isinstance(databases, dict) else None
    return default if isinstance(default, dict) else None


def _host_problems(settings, database):
    cassandraHeads = getattr(settings, 'CASSANDRA_HEAD', None) or [None]
    if isinstance(cassandraHeads, str):
        cassandraHeads = [cassandraHeads]
    if not isinstance(cassandraHeads, (list, tuple, set)):
        return ['CASSANDRA_HEAD must be a list of hosts, not %r' % (cassandraHeads,)]
    hosts = {'DB_HOST': [getattr(settings, 'DB_HOST', None)],
             'LOCAL_DB_HOST': [getattr(settings, 'LOCAL_DB_HOST', None)],
             "DATABASES['default']['HOST']": [database.get('HOST')],
             'CASSANDRA_HEAD': list(cassandraHeads)}
    return ['%s must be a loopback host, not %r' % (name, host)
            for name, values in hosts.items() for host in values if host not in LOOPBACK_HOSTS]


def _database_problems(settings, database):
    expected = {'DB_DATABASE': (getattr(settings, 'DB_DATABASE', None), DEV_DATABASE),
                'LOCAL_DB_DATABASE': (getattr(settings, 'LOCAL_DB_DATABASE', None), DEV_DATABASE),
                "DATABASES['default']['NAME']": (database.get('NAME'), DEV_DATABASE),
                "DATABASES['default']['USER']": (database.get('USER'), DEV_DB_USER),
                'DB_USER_READWRITE': (getattr(settings, 'DB_USER_READWRITE', None), DEV_DB_USER),
                'LOCAL_DB_USER': (getattr(settings, 'LOCAL_DB_USER', None), DEV_DB_USER),
                'DB_USER_READONLY': (getattr(settings, 'DB_USER_READONLY', None), DEV_DB_USER_READONLY),
                'DB_PORT': (getattr(settings, 'DB_PORT', None), DEV_DB_PORT),
                "DATABASES['default']['PORT']": (database.get('PORT'), DEV_DB_PORT)}
    return ['%s must be %r, not %r' % (name, want, value)
            for name, (value, want) in expected.items() if value != want]


def _migration_problems(settings):
    modules = getattr(settings, 'MIGRATION_MODULES', None)
    modules = modules if isinstance(modules, dict) else {}
    problems = ['MIGRATION_MODULES[%r] must start with %r' % (app, DEV_MIGRATIONS_PACKAGE)
                for app in APPS_WITH_DEV_MIGRATIONS
                if not isinstance(modules.get(app), str) or not modules[app].startswith(DEV_MIGRATIONS_PACKAGE)]
    # A VALUE OF None TURNS AN APP'S MIGRATIONS OFF (DJANGO DEBUG TOOLBAR DOES THIS), WHICH IS SAFE
    problems += ['MIGRATION_MODULES[%r] must be None or start with %r, not %r' % (app, DEV_MIGRATIONS_PACKAGE, module)
                 for app, module in modules.items() if app not in APPS_WITH_DEV_MIGRATIONS and module is not None
                 and not (isinstance(module, str) and module.startswith(DEV_MIGRATIONS_PACKAGE))]
    return problems


def dev_settings_problems(settings):
    """Return a list of reasons why `settings` is not the local dev stack (empty if it is).

    Only the `default` Django database is checked; the dev settings define no other.
    """
    problems = []
    settingsFile = os.path.realpath(getattr(settings, '__file__', '') or '')
    if settingsFile != os.path.realpath(DEV_SETTINGS_FILE):
        problems.append('settings were loaded from %r, not %r (does another settings.py come first on '
                        'sys.path?)' % (settingsFile, DEV_SETTINGS_FILE))
    if getattr(settings, 'LASAIR_DEV_STACK', False) is not True:
        problems.append('LASAIR_DEV_STACK is not True (run `make settings`)')
    database = _default_database(settings)
    if database is None:
        problems.append("DATABASES['default'] is missing")
        database = {}
    return (problems + _database_problems(settings, database) + _host_problems(settings, database)
            + _migration_problems(settings))


def environment_problems(environ):
    """Return reasons why the environment would make Django load other settings (empty if none)."""
    selected = environ.get('DJANGO_SETTINGS_MODULE')
    if selected not in (None, DJANGO_SETTINGS_NAME):
        return ['DJANGO_SETTINGS_MODULE is %r; unset it or set it to %r' % (selected, DJANGO_SETTINGS_NAME)]
    return []


def assert_dev_settings(settings, environ=None):
    """Raise RuntimeError, listing every problem, unless `settings` is the local dev stack."""
    problems = dev_settings_problems(settings) + environment_problems(os.environ if environ is None else environ)
    if problems:
        raise RuntimeError('Refusing to run: these are not the local dev settings.\n  - '
                           + '\n  - '.join(problems))


def _load_settings():
    os.chdir(paths.WEBSERVER_ROOT)
    import settings
    return settings


def setup_dev_django():
    """Check the dev settings, then set up Django with them. Return the settings module."""
    settings = _load_settings()
    assert_dev_settings(settings)
    os.environ['DJANGO_SETTINGS_MODULE'] = DJANGO_SETTINGS_NAME
    import django
    django.setup()
    return settings


def main():
    try:
        assert_dev_settings(_load_settings())
    except Exception as exc:  # ANY FAILURE TO LOAD OR CHECK THE SETTINGS MUST STOP THE MAKE TARGET
        print('%s: %s' % (type(exc).__name__, exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
