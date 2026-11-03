"""
Check that the log file was recently updated
If not, shout on slack

Run with a crontab, example here every 6 hours
0 */6 * * *  (cd /home/ubuntu/lasair4/services; python3 checklog.py)

This code can only run on an ingest or filter node
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
    """ discover if the log file is less than an hour old
        returns True or False
    """
    file_path = Path(f'/home/ubuntu/logs/{component}.log')

    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)

    if datetime.now() - modified_time <= timedelta(hours=1):
        return True
    else:
        return False

def shout_on_slack(message):
    """ post a message to slack channel
    """
    channel = '#general'
    _send(settings.SLACK_URL, message, channel)

if __name__ == "__main__":
    # example hostname lasair-ztf-ingest-0
    hostname = socket.gethostname()
    tok = hostname.split('-')
    # component name is either ingest or filter
    component = tok[2]

    if not is_fresh(component):
        message = f'Log file on {component} is stale'
        shout_on_slack(message)
