"""Tests for the check that dev tools only run against the local dev stack."""
import types
import unittest

from seed.guard import (APPS_WITH_DEV_MIGRATIONS, DEV_DATABASE, DEV_DB_PORT, DEV_DB_USER, DEV_DB_USER_READONLY,
                        DEV_SETTINGS_FILE, main, assert_dev_settings, dev_settings_problems,
                        environment_problems)

DEV_MIGRATION_MODULES = {app: 'dev_migrations.' + app for app in APPS_WITH_DEV_MIGRATIONS}


def _settings(**overrides):
    values = {
        '__file__': DEV_SETTINGS_FILE,
        'LASAIR_DEV_STACK': True,
        'DB_DATABASE': DEV_DATABASE,
        'LOCAL_DB_DATABASE': DEV_DATABASE,
        'DB_HOST': '127.0.0.1',
        'LOCAL_DB_HOST': '127.0.0.1',
        'DB_PORT': DEV_DB_PORT,
        'DB_USER_READWRITE': DEV_DB_USER,
        'LOCAL_DB_USER': DEV_DB_USER,
        'DB_USER_READONLY': DEV_DB_USER_READONLY,
        'DATABASES': {'default': {'NAME': DEV_DATABASE, 'HOST': '127.0.0.1', 'USER': DEV_DB_USER,
                                  'PORT': DEV_DB_PORT}},
        'CASSANDRA_HEAD': ['127.0.0.1'],
        'MIGRATION_MODULES': dict(DEV_MIGRATION_MODULES),
    }
    values.update(overrides)
    module = types.ModuleType('settings')
    for key, value in values.items():
        setattr(module, key, value)
    return module


class DevSettingsGuardTest(unittest.TestCase):

    def test_accepts_the_dev_settings(self):
        self.assertEqual(dev_settings_problems(_settings()), [])
        assert_dev_settings(_settings())

    def test_rejects_settings_without_the_dev_marker(self):
        settings = _settings()
        del settings.LASAIR_DEV_STACK
        self.assertIn('LASAIR_DEV_STACK', ' '.join(dev_settings_problems(settings)))

    def test_rejects_the_production_database_name(self):
        self.assertTrue(dev_settings_problems(_settings(DB_DATABASE='ztf')))
        self.assertTrue(dev_settings_problems(_settings(
            DATABASES={'default': {'NAME': 'ztf', 'HOST': '127.0.0.1', 'USER': DEV_DB_USER,
                                   'PORT': DEV_DB_PORT}})))

    def test_rejects_remote_database_and_cassandra_hosts(self):
        self.assertTrue(dev_settings_problems(_settings(DB_HOST='db.example.org')))
        self.assertTrue(dev_settings_problems(_settings(CASSANDRA_HEAD=['127.0.0.1', '10.0.0.5'])))

    def test_rejects_migrations_outside_dev_migrations(self):
        self.assertTrue(dev_settings_problems(_settings(MIGRATION_MODULES={})))
        self.assertTrue(dev_settings_problems(_settings(
            MIGRATION_MODULES=dict(DEV_MIGRATION_MODULES, watchlist='lasair.apps.watchlist.migrations'))))

    def test_requires_dev_migrations_for_every_unmigrated_app(self):
        problems = dev_settings_problems(_settings(MIGRATION_MODULES={'debug_toolbar': None}))
        for app in APPS_WITH_DEV_MIGRATIONS:
            self.assertIn(app, ' '.join(problems))

    def test_accepts_apps_with_migrations_turned_off(self):
        modules = dict(DEV_MIGRATION_MODULES, debug_toolbar=None)
        self.assertEqual(dev_settings_problems(_settings(MIGRATION_MODULES=modules)), [])

    def test_rejects_a_settings_module_from_another_file(self):
        self.assertTrue(dev_settings_problems(_settings(__file__='/repo/common/settings.py')))

    def test_rejects_another_database_user_or_port(self):
        self.assertIn('USER', ' '.join(dev_settings_problems(_settings(
            DATABASES={'default': {'NAME': DEV_DATABASE, 'HOST': '127.0.0.1', 'USER': 'ztf', 'PORT': DEV_DB_PORT}}))))
        self.assertIn('DB_PORT', ' '.join(dev_settings_problems(_settings(DB_PORT=3307))))
        self.assertIn('DB_USER_READWRITE', ' '.join(dev_settings_problems(_settings(DB_USER_READWRITE='ztf'))))
        self.assertIn('LOCAL_DB_USER', ' '.join(dev_settings_problems(_settings(LOCAL_DB_USER='ztf'))))
        self.assertIn('DB_USER_READONLY', ' '.join(dev_settings_problems(_settings(DB_USER_READONLY='ztf'))))

    def test_reports_a_cassandra_head_that_is_not_a_list(self):
        self.assertIn('CASSANDRA_HEAD', ' '.join(dev_settings_problems(_settings(CASSANDRA_HEAD=9042))))

    def test_main_exits_1_with_a_message_when_settings_fail_to_load(self):
        from unittest import mock
        with mock.patch('seed.guard._load_settings', side_effect=SyntaxError('bad settings')), \
                mock.patch('sys.stderr') as stderr:
            self.assertEqual(main(), 1)
        self.assertIn('bad settings', ''.join(str(c) for c in stderr.write.call_args_list))

    def test_reports_malformed_settings_instead_of_crashing(self):
        settings = _settings(CASSANDRA_HEAD='127.0.0.1', MIGRATION_MODULES={'watchlist': 7})
        del settings.DATABASES
        problems = ' '.join(dev_settings_problems(settings))
        self.assertIn("DATABASES['default']", problems)
        self.assertIn('MIGRATION_MODULES', problems)
        self.assertNotIn('CASSANDRA_HEAD', problems)

    def test_accepts_a_symlinked_path_to_the_dev_settings(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            link = os.path.join(tmp, 'settings.py')
            os.symlink(DEV_SETTINGS_FILE, link)
            self.assertEqual(dev_settings_problems(_settings(__file__=link)), [])

    def test_environment_must_not_select_another_settings_module(self):
        self.assertEqual(environment_problems({'LASAIR_DEV_STACK': '1'}), [])
        self.assertEqual(environment_problems({'LASAIR_DEV_STACK': '1', 'DJANGO_SETTINGS_MODULE': 'settings'}), [])
        self.assertTrue(environment_problems({'LASAIR_DEV_STACK': '1', 'DJANGO_SETTINGS_MODULE': 'lasair.prod'}))

    def test_assert_raises_with_every_problem_listed(self):
        with self.assertRaises(RuntimeError) as caught:
            assert_dev_settings(_settings(DB_DATABASE='ztf', DB_HOST='db.example.org'))
        self.assertIn('DB_DATABASE', str(caught.exception))
        self.assertIn('DB_HOST', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
