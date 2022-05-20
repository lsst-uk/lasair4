import sys
sys.path.append('../common')
from src import db_connect
sys.path.append('../webserver/lasair')
from query_builder import check_query, build_query

def check_query_syntax(msl, mq_id):
    message = 'checking query %d' % mq_id
    query = 'SELECT selected, conditions, tables FROM myqueries WHERE mq_id=%d'
    query = query % mq_id
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)
    for row in cursor:
        s = row['selected']
        f = row['tables']
        w = row['conditions']
        break

    e = check_query(s, f, w)
    if e:
        print(e)
    else:
        real_sql = build_query(s, f, w)
#        print(real_sql)

    try:
        cursor.execute(real_sql + ' LIMIT 0')
        message += ' --> OK'
    except Exception as e:
#        message += 'Your query:<br/><b>' + real_sql + '</b><br/>returned the error<br/><i>' + str(e) + '</i>'
        message += ' ' + str(e)
    return message

if __name__ == "__main__":
    msl = db_connect.readonly()
    if len(sys.argv) > 1:
        mq_id = int(msl, sys.argv[1])
        message = check_query_syntax(mq_id)
        print(message)
    else:
        query = 'SELECT mq_id FROM myqueries ORDER BY mq_id'
        cursor = msl.cursor(buffered=True, dictionary=True)
        cursor.execute(query)
        for row in cursor:
            message = check_query_syntax(msl, row['mq_id'])
            print(message)

