"""
Ingest proess runner. Sends args to its child and logs the outputs.
SIGTERM is passed to those children and dealt with properly.
Usage:
    ingest.py [--maxalert=MAX]
              [--group_id=GID]
              [--topic_in=TIN]

Options:
    --maxalert=MAX     Number of alerts to process, default is infinite
    --group_id=GID     Group ID for kafka, default is from settings
    --topic_in=TIN     Kafka topic to use, or
"""

import os, sys, time
sys.path.append('../../common')
import settings
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from src import slack_webhook
from docopt import docopt
import signal

stop = False

def sigterm_handler(signum, frame):
    global stop
    print('Stopping by SIGTERM')
    stop = True

signal.signal(signal.SIGTERM, sigterm_handler)

def now():
    # current UTC as string
    return datetime.utcnow().strftime("%Y/%m/%dT%H:%M:%S")

# where the log files go
log = open('/home/ubuntu/logs/ingest.log', 'a')

# Deal with arguments
my_args = docopt(__doc__)
child_args = []
for k, v in my_args.items():
    if v != None:
        child_args.append('%s=%s' % (k,v))


if not os.path.isfile(settings.LOCKFILE):
    print('Lockfile not present, exiting')
    sys.exit(0)

while not stop:
    rtxt = '======================\nFilter_runner at %s' % now()
    log.write('%s\n'% rtxt)
    print(rtxt)

    # start the process
    process = Popen(['python3', 'filter.py'] + child_args, stdout=PIPE, stderr=STDOUT)

    while 1:
        rbin = process.stdout.readline()

        # if the worker uses 'print', there will be at least the newline
        rtxt = rbin.decode('utf-8').rstrip()
        if len(rtxt) > 0:
            print('%s'% rtxt)
            log.write('%s\n'% rtxt)
            log.flush()
        else:
            break

        # scream to the humans if ERROR
        if 'ERROR' in rtxt:
            slack_webhook.send(settings.SLACK_URL, rtxt)
            time.sleep(settings.WAIT_TIME)

    process.wait()
    retcode = process.returncode

    # all the processes have done their batch
    if not os.path.isfile(settings.LOCKFILE):
        print('Lockfile not present, exiting')
        sys.exit(0)
    
    if retcode == 0:   # process got no alerts
        print('Waiting for more alerts ....')
        log.write('Waiting for more alerts ....\n')
        time.sleep(settings.WAIT_TIME)

print('Exiting')
