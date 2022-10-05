import sys
from subprocess import Popen, PIPE
sys.path.append('../common')
import settings
from src import slack_webhook

def execute_cmd(cmd, logfile=None):
    """ Executes a command like os.system, puts stdout into the log file
    and writes to slack if exception as well as non-zero return code
    """

    process = Popen([cmd], stdout=PIPE, stderr=PIPE, shell=True)
    out, err = process.communicate()
    out = out.decode('utf8')
    err = err.decode('utf8')

    if logfile:
        f = open(logfile, 'a')
        f.write(out)
        f.close
    else:
        print('%s' % out)

    if len(err) > 0:
        s = 'ERROR:' + err
        slack_webhook.send(settings.SLACK_URL, s)

    return process.returncode

if __name__ == "__main__":
    # run smoothly
    cmd = 'ls -l /mnt/cephfs/lasair'
    ret = execute_cmd(cmd, 'junk')
    print('returns ', ret)

    # will cause error
    cmd = 'ls -l /mnt/nosuchdirectory'
    ret = execute_cmd(cmd, 'junk')
    print('returns ', ret)

