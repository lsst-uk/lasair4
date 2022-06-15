import sys, time, json
sys.path.append('../../../common')
from src import db_connect
import settings
from build import get_cassandra_session, get_mysql_attrs, rebuild_features

def main():
    global cassandra_session, schema_names

    jdmax_min   = 2459550.68
    jdmax_max   = 2459550.70
    output      = 'csvfiles/output.csv'

    if len(sys.argv) > 3:
        jdmax_min = float(sys.argv[1])
        jdmax_max = float(sys.argv[2])
        output = sys.argv[3]
    print('jdmax_min %.2f jdmax_max %.2f' % (jdmax_min, jdmax_max))
    
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    
    query = "SELECT objects.objectId FROM objects "
    query += "WHERE jdmax > %f and jdmax < %f " % (jdmax_min, jdmax_max)
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

    f = open(output, 'w')
    f.write(csvlines)
    f.close()

    if nobject ==  0:
        print('no objects found')
        sys.exit(1)

    t = time.time() - t
    print('%d objects in %.1f msec each' % (nobject, t*1000.0/nobject))

    cassandra_session.shutdown()

if __name__ == "__main__":
    main()
