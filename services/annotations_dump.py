import sys, os
sys.path.append('../common/')
import settings
from datetime import datetime
today = datetime.today().strftime('%Y%m%d')
logfile = settings.SERVICES_LOG +'/'+ today + '.log'

cmd = 'echo "\\n-- dump annotations master at %s" >> %s'
cmd = cmd % (today, logfile)
os.system(cmd)

if not os.path.exists(settings.ANNOTATIONS_DUMP):
    os.makedirs(settings.ANNOTATIONS_DUMP)

cmd = 'mysqldump -u %s -p%s --port=%s --host=lasair-dev-db ztf annotations > %s/annotations.sql'
cmd = cmd % (settings.DB_USER_READWRITE, settings.DB_PASS_READWRITE, settings.DB_PORT, settings.ANNOTATIONS_DUMP)
os.system(cmd)

cmd = 'mysql -u %s -p%s --port=%s --host=%s ztf -e "select count(*) from annotations" >> %s'
cmd = cmd % (settings.DB_USER_READONLY, settings.DB_PASS_READONLY, settings.DB_PORT, settings.DB_HOST, logfile)
os.system(cmd)

cmd = 'ls -l %s/annotations.sql >> %s'
cmd = cmd % (settings.ANNOTATIONS_DUMP, logfile)
os.system(cmd)
