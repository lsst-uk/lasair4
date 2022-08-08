import os,sys, time
sys.path.append('../../common')
from datetime import datetime
from subprocess import Popen, PIPE
import settings
from src import date_nid, slack_webhook
import signal

""" Fire up the the ingestion and keep the results in a log file
    the start it again afte a minute or so
"""

# If we catch a SIGTERM, set a flag
sigterm_raised = False

def sigterm_handler(signum, frame):
    global sigterm_raised
    sigterm_raised = True

signal.signal(signal.SIGTERM, sigterm_handler)

def now():
    # current UTC as string
    return datetime.utcnow().strftime("%Y/%m/%dT%H:%M:%S")

while 1:
    if len(sys.argv) > 1:
        nid = int(sys.argv[1])
    else:
        nid  = date_nid.nid_now()
    date = date_nid.nid_to_date(nid)
    topic  = 'ztf_' + date + '_programid1'
    log = open('/home/ubuntu/logs/' + topic + '.log', 'a')
    if sigterm_raised:
        log.write("Caught SIGTERM, exiting.")
        sys.exit(0)

    if os.path.isfile(settings.LOCKFILE):
        args = ['python3', 'ingest.py', '--nid=%d'%nid]

        process = Popen(args, stdout=PIPE, stderr=PIPE)

        while 1:
            # when the worker terminates, readline returns zero
            rbin = process.stdout.readline()
            if len(rbin) == 0: break
    
            # if the worher uses 'print', there will be at least the newline
            rtxt = rbin.decode('utf-8').rstrip()
            log.write(rtxt + '\n')

            # scream to the humans if ERROR
            if rtxt.startswith('ERROR'):
                slack_webhook.send(settings.SLACK_URL, rtxt)

        while 1:
            # same with stderr
            rbin = process.stderr.readline()
            if len(rbin) == 0: break

            # if the worher uses 'print', there will be at least the newline
            rtxt = 'stderr:' + rbin.decode('utf-8').rstrip()
            log.write(rtxt + '\n')
            print(rtxt)

        process.wait()
        rc = process.returncode
    
        if rc == 0:  # no more to get
            log.write("END waiting %d seconds ...\n\n" % settings.WAIT_TIME)
            time.sleep(settings.WAIT_TIME)
        else:
            log.write("END getting more ...\n\n")
        log.close()
    else:
        # wait until the lockfile reappears
        rtxt = 'Waiting for lockfile ' + now()
        print(rtxt)
        log.write(rtxt + '\n')
        time.sleep(settings.WAIT_TIME)
