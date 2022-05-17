import sys, os
sys.path.append('../../common/')
import settings
from datetime import datetime
today = datetime.today().strftime('%Y%m%d')
logfile = settings.SERVICES_LOG +'/'+ today + '.log'

cmd = 'echo "\\n-- fetch crossmatch_tns at %s" >> %s'
cmd = cmd % (today, logfile)
os.system(cmd)

cmd = 'mysql -u ztf -p ztf -p%s < %s/crossmatch_tns.sql'
cmd = cmd % (settings.LOCAL_DB_PASS, settings.CROSSMATCH_TNS_DUMP)
os.system(cmd)

cmd = 'mysql -u ztf -p%s ztf -e "select count(*) from crossmatch_tns" >> %s'
cmd = cmd % (settings.LOCAL_DB_PASS, logfile)
os.system(cmd)
