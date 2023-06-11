import sys
sys.path.append('../common')
from src import db_connect
sys.path.append('../webserver/lasair')
from query_builder import check_query, build_query

def check_query_syntax(mq_id, verbose=False, update=False):
    msl = db_connect.remote()
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
<<<<<<< HEAD
        real_sql = build_query(s, f, w)
        if verbose:
            print(real_sql)
=======
        try:
            real_sql = build_query(s, f, w)
        except Exception as e:
            message = 'Query building failed %s\n%s\n%s\n%s\n' % (str(e), s, f, w)
            return message
#        print(real_sql)
>>>>>>> ef6411b7f8519dbf061ab7b667ff23bd076c0d11
    try:
        cursor.execute(real_sql + ' LIMIT 0')
        message += ' --> OK'
        good = True
    except Exception as e:
        message += ' ' + str(e)
        good = False

    if update and good:
        query = "UPDATE myqueries SET real_sql='%s' WHERE mq_id=%d" % (real_sql, mq_id)
        print(query)
        cursor.execute(query)
        msl.commit()
        message += ' real_sql updated'
    return message

if __name__ == "__main__":
    # if there is a specific query, check it and update it
    if len(sys.argv) > 1:
        mq_id = int(sys.argv[1])
        message = check_query_syntax(mq_id, verbose=True, update=True)
        print(message)

    # if no specific query, just check them all
    else:
        query = 'SELECT mq_id FROM myqueries ORDER BY mq_id'
        msl = db_connect.remote()
        cursor = msl.cursor(buffered=True, dictionary=True)
        cursor.execute(query)
        for row in cursor:
            message = check_query_syntax(row['mq_id'], verbose=False, update=False)
            print(message)

