""" To be run in as 'screen' session that continuously fetches batches
"""
import os, sys, time
sys.path.append('../../common')
import settings
from datetime import datetime
from subprocess import Popen, PIPE
from src import lasairLogging, slack_webhook
import signal

# If we catch a SIGTERM, set a flag
sigterm_raised = False


def sigterm_handler(signum, frame):
    global sigterm_raised
    sigterm_raised = True


signal.signal(signal.SIGTERM, sigterm_handler)


def now():
    # current UTC as string
    return datetime.utcnow().strftime("%Y/%m/%dT%H:%M:%S")


# Set up the logger
lasairLogging.basicConfig(
    # TODO: Why is this called ingest.log? Can we rename it to filter.log or filter_runner.log?
    filename='/home/ubuntu/logs/ingest.log',
    webhook=slack_webhook.SlackWebhook(url=settings.SLACK_URL),
    merge=True
)
log = lasairLogging.getLogger("filter_runner")

while 1:
    if sigterm_raised:
        log.info("Caught SIGTERM, exiting.")
        lasairLogging.shutdown()
        sys.exit(0)

    if os.path.isfile(settings.LOCKFILE):
        # args on the command line passed to filter.py
        args = ['python3', 'filter.py'] + sys.argv[1:]
        log.info('------', now())
        process = Popen(args, stdout=PIPE, stderr=PIPE)

        while 1:
            # when the worker terminates, readline returns zero
            rbin = process.stdout.readline()
            if len(rbin) == 0: break

            # if the worker uses 'print', there will be at least the newline
            rtxt = rbin.decode('utf-8').rstrip()
            if rtxt.startswith('ERROR'):
                log.error(rtxt)
            else:
                log.info(rtxt)

        while 1:
            # same with stderr
            rbin = process.stderr.readline()
            if len(rbin) == 0: break

            # if the worker uses 'print', there will be at least the newline
            rtxt = 'stderr:' + rbin.decode('utf-8').rstrip()
            log.warning(rtxt)


        process.wait()
        rc = process.returncode

        # if we timed out of kafka, wait a while and ask again
        log.info(now())
        if rc > 0:  # try again
            log.info("END getting more ...\n")
        # else just go ahead immediately
        elif rc == 0:
            log.info("END waiting %d seconds ...\n" % settings.WAIT_TIME)
            for i in range(settings.WAIT_TIME):
                if sigterm_raised:
                    log.info("Caught SIGTERM, exiting.")
                    lasairLogging.shutdown()
                    sys.exit(0)
                time.sleep(1)
        else:   # rc < 0
            log.warning("STOP on error!")
            lasairLogging.shutdown()
            sys.exit(1)

    else:
        # wait until the lockfile reappears
        rtxt = 'Waiting for lockfile ' + now()
        log.info(rtxt)
        time.sleep(settings.WAIT_TIME)

