import sys, os
sys.path.append('../common/')
import settings
from datetime import datetime
today = datetime.today().strftime('%Y%m%d')
logfile = settings.SERVICES_LOG +'/'+ today + '.log'

cmd = 'echo "\\n-- mysql backup at %s" >> %s'
cmd = cmd % (today, logfile)
os.system(cmd)

cmd = 'ssh %s sudo mysqldump -u root -p%s --port=%s ztf > %s/mysqlbackup.sql'
cmd = cmd % (settings.DB_HOST, settings.DB_ROOT_PASS, settings.DB_PORT, settings.MYSQL_BACKUP_DIR)
print(cmd)
os.system(cmd)

cmd = 'ls -l %s >> %s'
cmd = cmd % (settings.MYSQL_BACKUP_DIR, logfile)
os.system(cmd)



