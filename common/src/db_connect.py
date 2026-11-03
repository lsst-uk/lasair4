import sys
sys.path.append('..')
import settings
import mysql.connector

# DATABASE NAMES DEFAULT TO 'ztf'; SETTINGS MAY OVERRIDE THEM (FOR EXAMPLE THE LOCAL DEV STACK)
DEFAULT_DATABASE = 'ztf'

def readonly():
    config = {
        'user'    : settings.DB_USER_READONLY,
        'password': settings.DB_PASS_READONLY,
        'host'    : settings.DB_HOST,
        'port'    : settings.DB_PORT,
        'database': getattr(settings, 'DB_DATABASE', DEFAULT_DATABASE)
    }
    return mysql.connector.connect(**config)

def remote():
    config = {
        'user'    : settings.DB_USER_READWRITE,
        'password': settings.DB_PASS_READWRITE,
        'host'    : settings.DB_HOST,
        'port'    : settings.DB_PORT,
        'database': getattr(settings, 'DB_DATABASE', DEFAULT_DATABASE)
    }
    return mysql.connector.connect(**config)

def local():
    config = {
        'user'    : settings.LOCAL_DB_USER,
        'password': settings.LOCAL_DB_PASS,
        'host'    : settings.LOCAL_DB_HOST,
        'database': getattr(settings, 'LOCAL_DB_DATABASE', DEFAULT_DATABASE)
    }
    return mysql.connector.connect(**config)
