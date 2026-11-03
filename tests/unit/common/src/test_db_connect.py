"""Unit tests for common/src/db_connect.py database-name selection."""
import importlib
import sys
import types
import unittest
from unittest import mock

import context  # noqa: F401  (PUTS common/src ON sys.path)


def _fake_settings(**extra):
    settings = types.ModuleType('settings')
    settings.DB_USER_READONLY = 'ro'
    settings.DB_PASS_READONLY = 'ro'
    settings.DB_USER_READWRITE = 'rw'
    settings.DB_PASS_READWRITE = 'rw'
    settings.DB_HOST = 'localhost'
    settings.DB_PORT = 3306
    settings.LOCAL_DB_USER = 'local'
    settings.LOCAL_DB_PASS = 'local'
    settings.LOCAL_DB_HOST = 'localhost'
    for key, value in extra.items():
        setattr(settings, key, value)
    return settings


def _load_db_connect(settings):
    connector = types.ModuleType('mysql.connector')
    connector.connect = mock.MagicMock(name='connect')
    mysql = types.ModuleType('mysql')
    mysql.connector = connector
    modules = {'settings': settings, 'mysql': mysql, 'mysql.connector': connector}
    with mock.patch.dict(sys.modules, modules):
        sys.modules.pop('db_connect', None)
        module = importlib.import_module('db_connect')
    sys.modules.pop('db_connect', None)
    return module, connector.connect


class DbConnectDatabaseNameTest(unittest.TestCase):
    def test_uses_ztf_when_settings_name_no_database(self):
        dbConnect, connect = _load_db_connect(_fake_settings())
        for fn in (dbConnect.readonly, dbConnect.remote, dbConnect.local):
            fn()
            self.assertEqual(connect.call_args.kwargs['database'], 'ztf')

    def test_uses_db_database_setting_for_master_connections(self):
        dbConnect, connect = _load_db_connect(_fake_settings(DB_DATABASE='lasair_dev'))
        dbConnect.readonly()
        self.assertEqual(connect.call_args.kwargs['database'], 'lasair_dev')
        dbConnect.remote()
        self.assertEqual(connect.call_args.kwargs['database'], 'lasair_dev')

    def test_uses_local_db_database_setting_for_local_connection(self):
        dbConnect, connect = _load_db_connect(_fake_settings(LOCAL_DB_DATABASE='lasair_dev_local'))
        dbConnect.local()
        self.assertEqual(connect.call_args.kwargs['database'], 'lasair_dev_local')


if __name__ == '__main__':
    unittest.main()
