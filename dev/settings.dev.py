"""
Django and Lasair settings for the local development stack.

`make settings` copies this file to `webserver/lasair/settings.py`. Every value
here is for a throwaway local stack. Do not use it on a shared or public host.
"""
import os
import sys

# THESE SETTINGS ONLY LOAD WHEN dev/Makefile (OR YOU) SETS LASAIR_DEV_STACK=1, SO A WSGI SERVER CANNOT PICK THEM UP
if os.environ.get('LASAIR_DEV_STACK') != '1':
    raise RuntimeError('These are the local dev settings. Run them through dev/Makefile, '
                       'or set LASAIR_DEV_STACK=1 if you mean to use them.')

# MARKS THESE AS THE LOCAL DEV SETTINGS; dev/seed/guard.py REFUSES TO RUN WITHOUT IT
LASAIR_DEV_STACK = True

# PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(BASE_DIR)
DEV_ROOT = os.path.join(REPO_ROOT, 'dev')
DEV_VAR = os.path.join(DEV_ROOT, 'var')

# SHARED HELPERS IN common/ AND THE GENERATED DEV-ONLY MIGRATIONS IN dev/var/
for extraPath in (os.path.join(REPO_ROOT, 'common'), DEV_VAR):
    if extraPath not in sys.path:
        sys.path.append(extraPath)


def _read_secret_key():
    keyPath = os.path.join(DEV_VAR, 'secret_key')
    try:
        with open(keyPath) as keyFile:
            return keyFile.read().strip()
    except FileNotFoundError as exc:
        raise RuntimeError(
            f'{keyPath} is missing. Run `make settings` in dev/ to create it.') from exc


SECRET_KEY = _read_secret_key()
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
INTERNAL_IPS = ['127.0.0.1']

# THE STATIC FILES PANEL REJECTS THE TEMPLATES' LEADING-SLASH PATHS ({% static '/img/...' %}), SO LEAVE IT OUT
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.history.HistoryPanel',
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.alerts.AlertsPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# LASAIR_URL OF 127.0.0.1 WITH DEBUG ON SKIPS THE RECAPTCHA CHECK (users/forms.py)
LASAIR_URL = '127.0.0.1'
WEB_DOMAIN = 'lasair-dev'
LASAIR_GRAFANA_URL = 'http://127.0.0.1:3000'

# DATABASES: LOCAL HOMEBREW MARIADB (SEE dev/db/bootstrap.sql)
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_DATABASE = 'lasair_dev'
LOCAL_DB_DATABASE = DB_DATABASE
DB_USER_READONLY = 'lasair_dev_ro'
DB_PASS_READONLY = 'lasair_dev_ro'
DB_USER_READWRITE = 'lasair_dev_rw'
DB_PASS_READWRITE = 'lasair_dev_rw'
READWRITE_USER = DB_USER_READWRITE
READWRITE_PASS = DB_PASS_READWRITE
READONLY_USER = DB_USER_READONLY
READONLY_PASS = DB_PASS_READONLY
LOCAL_DB_USER = DB_USER_READWRITE
LOCAL_DB_PASS = DB_PASS_READWRITE
LOCAL_DB_HOST = DB_HOST

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_DATABASE,
        'USER': READWRITE_USER,
        'PASSWORD': READWRITE_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# LIGHTCURVES: CASSANDRA CONTAINER (SEE dev/Makefile cassandra-up)
CASSANDRA_HEAD = ['127.0.0.1']

# FILE STORES
IMAGEFITS = os.path.join(DEV_VAR, 'fits')
KAFKA_STREAMS = os.path.join(DEV_VAR, 'streams')
SYSTEM_STATUS = os.path.join(DEV_VAR, 'system_status', 'status')
MEDIA_ROOT = os.path.join(DEV_VAR, 'media')
MEDIA_URL = '/media/'
FRONT_PAGE_CACHE = os.path.join(DEV_VAR, 'front_page_cache.json')
FRONT_PAGE_STALE = 60
LASAIR_ROOT = DEV_VAR
QUERY_CACHE = os.path.join(DEV_VAR, 'query_cache')
BLOB_STORE_ROOT = os.path.join(DEV_VAR, 'blob')

# SERVICES THAT DO NOT RUN LOCALLY. CALLS TO THEM FAIL, WHICH IS EXPECTED.
PUBLIC_KAFKA_SERVER = '127.0.0.1:9092'
PUBLIC_KAFKA_PRODUCER = '127.0.0.1:9092'
PUBLIC_KAFKA_PASSWORD = 'not-used-locally'
INTERNAL_KAFKA_PRODUCER = '127.0.0.1:9092'
ANNOTATION_TOPIC_OUT = 'ztf_annotations'
SHERLOCK_SERVICE = '127.0.0.1:5001'

# LIMITS
WATCHLIST_MAX = 10
WATCHLIST_MAX_CROSSMATCH = 1000
ACTIVE_EXPIRE = 180
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400

# THE SEEDED __TNS__ WATCHLIST (dev/seed/context.py)
TNS_WATCHLIST_ID = 1

# EMAIL IS PRINTED TO THE CONSOLE
DEFAULT_FROM_EMAIL = 'donotreply@lasair-dev.local'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# GOOGLE'S PUBLIC RECAPTCHA TEST KEYS
RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-zFI6KIykyLSKqUvHgD0hBn5D'
RECAPTCHA_REQUIRED_SCORE = 0.7
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

INSTALLED_APPS = [
    'users.apps.UsersConfig',
    'captcha',
    'crispy_forms',
    'crispy_bootstrap5',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'lasair',
    'lasair.apps.annotator',
    'lasair.apps.db_schema',
    'lasair.apps.filter_query',
    'lasair.apps.multimessenger_map',
    'lasair.apps.object',
    'lasair.apps.search',
    'lasair.apps.status',
    'lasair.apps.watchlist',
    'lasair.apps.watchmap',
    'lasairapi',
    'django.contrib.admin',
    'rest_framework',
    'rest_framework.authtoken',
    'debug_toolbar',
    'widget_tweaks',
    'django_browser_reload',
]

# THESE THREE APPS HAVE NO MIGRATIONS IN GIT. THE DEV STACK GENERATES THEM INTO
# dev/var/dev_migrations SO PRODUCTION MIGRATION HISTORY IS NOT TOUCHED.
MIGRATION_MODULES = {
    'watchlist': 'dev_migrations.watchlist',
    'watchmap': 'dev_migrations.watchmap',
    'filter_query': 'dev_migrations.filter_query',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.UserRateThrottle',
        'lasairapi.throttle.UserClassRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {'user': '1000000/hour', },
    'EXCEPTION_HANDLER': 'lasairapi.throttle.custom_exception_handler',
    'ANON_THROTTLE_RATES': {'user': '1000/hour', },
    'USER_THROTTLE_RATES': {'user': '100000/hour', },
    'POWER_THROTTLE_RATES': {'user': '1000000/hour', },
}

ROOT_URLCONF = 'lasair.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'lasair', 'templates'),
            os.path.join(BASE_DIR, 'lasairapi', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'lasair.context_processors.dev',
                'lasair.context_processors.cfg_assets_root',
                'lasair.context_processors.global_vars'
            ],
        },
    },
]
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

WSGI_APPLICATION = 'lasair.wsgi.application'

LOGIN_REDIRECT_URL = 'index'
LOGIN_URL = 'login'

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

STATIC_URL = '/lasair/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'staticfiles/build'),)
ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/lasair/static')
