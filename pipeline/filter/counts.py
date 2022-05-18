import sys
sys.path.append('../../common')
import settings
from src import db_connect

import requests
import urllib
import urllib.parse
import json
import time
import math
import datetime

def since_midnight():
    """since_midnight.
    How many objects updated since last midnight
    """
    t = time.time()
    jdnow = (time.time()/86400 + 2440587.5)
    midnight = math.floor(jdnow - 0.5) + 0.5

    msl = db_connect.readonly()
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT count(*) AS count FROM objects WHERE jdmax > %.1f' % midnight
    try:
        cursor.execute(query)
        for row in cursor:
            count = row['count']
            break
    except:
        count = -1

    query = 'SELECT jdnow()-max(jdmax) AS delay FROM objects'
    try:
        cursor.execute(query)
        for row in cursor:
            delay = 24*row['delay']
            h = int(delay)
            m = int((delay-h)*60)
            delay = '%d:%02d' % (h,m)
            break
    except:
        delay = -1.0

    query = 'SELECT count(*) AS total_count FROM objects'
    try:
        cursor.execute(query)
        for row in cursor:
            total_count = row['total_count']
            break
    except:
        total_count = -1
    return {'count':count, 'delay':delay, 'total_count':total_count}

def grafana_today():
    """since_midnight.
    How many objects reported today from ZTF
    """
    g = datetime.datetime.utcnow()
    date = '%4d%02d%02d' % (g.year, g.month, g.day)
    url = 'https://monitor.alerts.ztf.uw.edu/api/datasources/proxy/7/api/v1/query?query='
    urltail = 'sum(kafka_log_log_value{ name="LogEndOffset" , night = "%s", program = "MSIP" }) - sum(kafka_log_log_value{ name="LogStartOffset", night = "%s", program="MSIP" })' % (date, date)
    
    try:
        urlquote = url + urllib.parse.quote(urltail)
        resultjson = requests.get(urlquote, 
            auth=(settings.GRAFANA_USERNAME, settings.GRAFANA_PASSWORD))
        result = json.loads(resultjson.text)
        alertsstr = result['data']['result'][0]['value'][1]
        today_candidates_ztf = int(alertsstr)
    except Exception as e:
        print('Cannot parse grafana: %s' % str(result))
        print(e)
        today_candidates_ztf = -1

    return today_candidates_ztf

if __name__ == "__main__":
    print('Grafana today:', grafana_today())
