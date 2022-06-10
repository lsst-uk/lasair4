import sys, os
sys.path.append('../common/')
import settings
from datetime import datetime
today = datetime.today().strftime('%Y%m%d')
logfile = settings.SERVICES_LOG +'/'+ today + '.log'

cmd = 'echo "\\n-- dump crossmatch_tns master at %s" >> %s'
cmd = cmd % (today, logfile)
os.system(cmd)

if not os.path.exists(settings.CROSSMATCH_TNS_DUMP):
    os.makedirs(settings.CROSSMATCH_TNS_DUMP)

cmd = 'mysqldump -u %s -p%s --port=%s --host=%s ztf crossmatch_tns > %s/crossmatch_tns.sql'
cmd = cmd % (settings.DB_USER_READWRITE, settings.DB_PASS_READWRITE, settings.DB_PORT, settings.DB_HOST, settings.CROSSMATCH_TNS_DUMP)
os.system(cmd)

cmd = 'mysql -u %s -p%s --port=%s --host=%s ztf -e "select count(*) from crossmatch_tns" >> %s'
cmd = cmd % (settings.DB_USER_READONLY, settings.DB_PASS_READONLY, settings.DB_PORT, settings.DB_HOST,  logfile)
os.system(cmd)

cmd = 'ls -l %s/crossmatch_tns.sql >> %s'
cmd = cmd % (settings.CROSSMATCH_TNS_DUMP, logfile)
os.system(cmd)
