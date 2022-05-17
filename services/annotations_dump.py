import sys, os
sys.path.append('../common/')
import settings
from datetime import datetime
today = datetime.today().strftime('%Y%m%d')
logfile = settings.SERVICES_LOG +'/'+ today + '.log'

cmd = 'echo "\\n-- dump annotations master at %s" >> %s'
cmd = cmd % (today, logfile)
os.system(cmd)

cmd = 'ssh %s sudo mysqldump -u root -p%s --port=%s ztf annotations > %s/annotations.sql'
cmd = cmd % (settings.DB_HOST, settings.DB_ROOT_PASS, settings.DB_PORT, settings.ANNOTATIONS_DUMP)
os.system(cmd)

cmd = 'mysql -u %s -p%s --port=%s --host=%s ztf -e "select count(*) from annotations" >> %s'
cmd = cmd % (settings.DB_USER_READONLY, settings.DB_PASS_READONLY, settings.DB_PORT, settings.DB_HOST, logfile)
os.system(cmd)

cmd = 'ls -l %s/annotations.sql >> %s'
cmd = cmd % (settings.ANNOTATIONS_DUMP, logfile)
os.system(cmd)
