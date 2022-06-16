"""
Rebuilds features for Lasair. Takes a start JD, end JD,
and makes CSV files suitable for ingestion with sister program csv_to_database.
Can run with multiprocessing.
Usage:
    runner.py [--nprocess=NP]
              (--sjd=SJD)
              (--ejd=EJD)
              (--out=OUT)

Options:
  --nprocess=NP    Number of processes to use [default: 1]
  --sjd=SJD        Start JD, example 2459550.68
  --ejd=EJD        End JD, example 2459550.70
  --out=OUT        Directory name for output
"""
import sys, time, json
sys.path.append('../../../common')
import settings
from src import db_connect
from docopt import docopt
from multiprocessing import Process, Manager
from build import get_cassandra_session, get_mysql_attrs, rebuild_features

def run(runargs):
    global cassandra_session, schema_names
    nprocess = int(runargs['--nprocess'])
    iprocess = int(runargs['--iprocess'])

    global_sjd = float(runargs['--sjd'])
    global_ejd = float(runargs['--ejd'])
    out = runargs['--out']

    dt = (global_ejd - global_sjd)/nprocess
    sjd = global_sjd + dt*iprocess
    ejd = global_sjd + dt*(iprocess+1)

    print('%d: start JD %.2f end JD %.2f' % (iprocess, sjd, ejd))
    
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    
    query = "SELECT objects.objectId FROM objects "
    query += "WHERE jdmax > %f and jdmax < %f " % (sjd, ejd)
#    query += "LIMIT 1000 "
    cursor.execute(query)

    cassandra_session = get_cassandra_session()
    schema_names = get_mysql_attrs(msl)

    t = time.time()
    nobject = 0
    objectList = []
    for row in cursor:
        objectList.append(row['objectId'])
    nobject = len(objectList)

    ndone = 0
    csvlines = ''
    for objectId in objectList:
        csvline = rebuild_features({
           'objectId': objectId,
           'schema_names': schema_names,
           'cassandra_session':cassandra_session,
        })
        if csvline:
            csvlines += csvline + '\n'
        ndone += 1
        #print(ndone, ' of ', nobject)

    f = open('%s/%07d_%07d_%s.csv' % (out, int(global_sjd), int(global_ejd), iprocess) , 'w')
    f.write(csvlines)
    f.close()

    if nobject ==  0:
        print('no objects found')
        sys.exit(1)

    t = time.time() - t
    print('%d %d objects in %.1f msec each' % (iprocess, nobject, t*1000.0/nobject))

    cassandra_session.shutdown()

if __name__ == "__main__":
    args = docopt(__doc__)
    nprocess = int(args['--nprocess'])
    print('Running %d processes' % nprocess)

    process_list = []
    for iprocess in range(nprocess):
        runargs = args.copy()
        runargs['--iprocess'] = iprocess
        p = Process(target=run, args=(runargs,))
        process_list.append(p)
        p.start()

    for p in process_list:
        p.join()
