import os, sys, time
sys.path.append('../../../common')
from src import db_connect
import settings

def handle(filename):
    sql  = "LOAD DATA LOCAL INFILE '%s' " % filename
    sql += "REPLACE INTO TABLE objects FIELDS TERMINATED BY ',' "
    sql += "ENCLOSED BY '\"' LINES TERMINATED BY '\n'"

    sqlfile = 'tmp.sql'
    f = open(sqlfile, 'w')
    f.write(sql)
    f.close()

    cmd =  "mysql --user=%s --database=ztf --password=%s --host=%s --port=%s < tmp.sql" 
    cmd = cmd % (settings.DB_USER_READWRITE, settings.DB_PASS_READWRITE, settings.DB_HOST, settings.DB_PORT)
    print(cmd)
    os.system(cmd)

################
csvfiles = sys.argv[1]

try:
    os.mkdir('tmp')
except:
    pass

filelist = os.listdir(csvfiles)
filelist.sort()

for csvfile in filelist:
    t = time.time()
    cmd = 'cd %s; split -l 100000 %s; mv x* ../tmp' % (csvfiles, csvfile)
    print(cmd)
    os.system(cmd)
    for tmpfile in os.listdir('tmp'):
        handle('tmp/' + tmpfile)
    os.system('rm tmp/*')
    print('%s imported in %.0f seconds' % (csvfile, (time.time() - t)))

