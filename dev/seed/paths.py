"""Put the repo's shared helper folders on sys.path.

Lasair code imports helpers by bare module name (for example `import settings`,
`from src import db_connect`, `from insert_query import ...`). Importing this
module makes those names resolve when the seed code runs from `dev/`.
"""
import os
import sys

DEV_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(DEV_ROOT)
WEBSERVER_ROOT = os.path.join(REPO_ROOT, 'webserver')

_EXTRA_PATHS = (
    os.path.join(REPO_ROOT, 'common'),
    os.path.join(REPO_ROOT, 'common', 'src'),
    os.path.join(REPO_ROOT, 'pipeline', 'filter', 'features_ZTF'),
    WEBSERVER_ROOT,
)
# THE DEV SETTINGS MUST WIN `import settings`, EVEN IF A PIPELINE common/settings.py EXISTS
DEV_SETTINGS_DIR = os.path.join(WEBSERVER_ROOT, 'lasair')

for extraPath in _EXTRA_PATHS:
    if extraPath not in sys.path:
        sys.path.append(extraPath)
if DEV_SETTINGS_DIR in sys.path:
    sys.path.remove(DEV_SETTINGS_DIR)
sys.path.insert(0, DEV_SETTINGS_DIR)
