import sys, os
sys.path.append('../common/')
import settings
from datetime import datetime
today = datetime.today().strftime('%Y%m%d')
logfile = settings.SERVICES_LOG +'/'+ today + '.log'

cmd = 'echo "\\n-- mysql backup at %s" >> %s'
cmd = cmd % (today, logfile)
os.system(cmd)

cmd = 'mysqldump -u %s -p%s --port=%s --host=%s ztf > %s/mysqlbackup.sql'
cmd = cmd % (settings.DB_USER_READWRITE, settings.DB_PASS_READWRITE, settings.BACKUP_DATABASE_PORT, settings.BACKUP_DATABASE_HOST, settings.MYSQL_BACKUP_DIR)
os.system(cmd)

cmd = 'ls -l %s >> %s'
cmd = cmd % (settings.MYSQL_BACKUP_DIR, logfile)
os.system(cmd)



