"""
Check that the log file was recently updated
If not, shout on slack
Run with a crontab, example every 6 hours
0 */6 * * *  (cd /home/ubuntu/lasair4/services; python3 checklog.py)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import socket

sys.path.append('../common')
import settings
sys.path.append('../common/src')
from slack_webhook import _send

def is_fresh(component):
    file_path = Path(f'/home/ubuntu/logs/{component}.log')

    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)

    if datetime.now() - modified_time <= timedelta(hours=1):
        return True
    else:
        return False

def shout_on_slack(message):
    channel = '#general'
    _send(settings.SLACK_URL, message, channel)

if __name__ == "__main__":
    hostname = socket.gethostname()
    tok = hostname.split('-')
    component = tok[2]
    if not is_fresh(component):
        message = f'Log file on {component} is stale'
        shout_on_slack(message)
