"""
Ingest proess runner. Takes the --nprocess arg and starts that many versions of ingest.py, 
with other arguments sent there, also logs the outputs. 
SIGTERM is passed to those children and dealt with properly.
Usage:
    ingest.py [--maxalert=MAX]
              [--nprocess=nprocess]
              [--group_id=GID]
              [--topic_in=TIN | --nid=NID]
              [--topic_out=TOUT]

Options:
    --maxalert=MAX     Number of alerts to process, default is infinite
    --nprocess=nprocess  Number of processes
    --group_id=GID     Group ID for kafka, default is from settings
    --topic_in=TIN     Kafka topic to use, or
    --nid=NID          ZTF night number to use (default today)
    --topic_out=TOUT   Kafka topic for output [default:ztf_sherlock]
"""
import os,sys, time
sys.path.append('../../common')
import settings
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from src import date_nid, slack_webhook
from docopt import docopt

# Our processes
process_list = []

# Deal with arguments
nprocess = 1
child_args = []
my_args = docopt(__doc__)

for k, v in my_args.items():
    # pick out the nprocess argument, thats mine
    if k == '--nprocess' and v != None:
        nprocess = int(v)

    # everything else gets sent to the children
    elif v != None:
        child_args.append('%s=%s' % (k,v))

print('ingest_runner with %d processes' % nprocess)

# The log file
log = open('/home/ubuntu/logs/ingest.log', 'a')

# start the processes
for i in range(nprocess):
    process = Popen(['python3', 'ingest.py'] + child_args, stdout=PIPE, stderr=STDOUT)
    process_list.append(process)

# read from them
while 1:
    n = 0
    for i in range(nprocess):
        # when the worker terminates, readline returns zero
        rbin = process_list[i].stdout.readline()
        if len(rbin) == 0:
            n += 1
  
        # if the worker uses 'print', there will be at least the newline
        rtxt = rbin.decode('utf-8').rstrip()
        if len(rtxt) > 0:
            log.write('%d: %s\n'% (i, rtxt))
            log.flush()

        # scream to the humans if ERROR
        if 'ERROR' in rtxt:
            slack_webhook.send(settings.SLACK_URL, rtxt)
            time.sleep(settings.WAIT_TIME)
    if n == nprocess:
        break

# wait for them to finish
for i in range(nprocess):
    process_list[i].wait()
