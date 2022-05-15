import os, sys
sys.path.append('../common')
import settings
from src import db_connect
from confluent_kafka import Producer, KafkaError, admin
from datetime import datetime
import time, json

def datetime_converter(o):
# used by json encoder when it gets a type it doesn't understand
    if isinstance(o, datetime):
        return o.__str__()

def topic_refresh(real_sql, topic, limit=10):
    message = ''
    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = real_sql + ' LIMIT %d' % limit

    try:
        cursor.execute(query)
    except Exception as e:
        message += 'Your query:<br/><b>' + query + '</b><br/>returned the error<br/><i>' + str(e) + '</i><br/>'
        return message

    recent = []
    for record in cursor:
        recorddict = dict(record)
        now_number = datetime.utcnow()
        recorddict['UTC'] = now_number.strftime("%Y-%m-%d %H:%M:%S")
        print(recorddict)
        recent.append(recorddict)

    conf = {
        'bootstrap.servers': settings.PUBLIC_KAFKA_SERVER,
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanisms'  : 'SCRAM-SHA-256',
        'sasl.username'    : 'admin',
        'sasl.password'    : settings.PUBLIC_KAFKA_PASSWORD
    }

    # delete the old topic
    a = admin.AdminClient(conf)

    try:
        result = a.delete_topics([topic])
        result[topic].result()
        time.sleep(1)
        message += 'Topic %s deleted<br/>' % topic
    except Exception as e:
        message += 'Topic is ' + topic + '<br/>'
        message += str(e) + '<br/>'

    # pushing in new messages will remake the topic
    try:
        p = Producer(conf)
        for out in recent: 
            jsonout = json.dumps(out, default=datetime_converter)
            p.produce(topic, value=jsonout)
        p.flush(10.0)   # 10 second timeout
        message += '%d new messages produced to topic %s<br/>' % (limit, topic)
    except Exception as e:
        message += "ERROR in queries/topic_refresh: cannot produce to public kafka<br/>" + str(e) + '<br/>'
    return message
