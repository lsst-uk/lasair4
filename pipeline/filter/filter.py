""" 
Filter code for Lasair. 
    fetch a batch of alerts from kafka
    run the watchlist code and insert the hits
    run the active user queries and produce kafka
    build a CSV file of three tables with the batch: 
      objects, sherlock_classifications, watchlist_hits, area_hits
    send data to main db with mysql --host

Usage:
    filter.py [--maxalert=MAX]
              [--group_id=GID]
              [--topic_in=TIN]

Options:
    --maxalert=MAX     Number of alerts to process, default is from settings.
    --group_id=GID     Group ID for kafka, default is from settings
    --topic_in=TIN     Kafka topic to use, default is from settings

"""
import os,sys, time, tempfile, confluent_kafka
from docopt import docopt
from socket import gethostname
from datetime import datetime

import run_active_queries
from check_alerts_watchlists import get_watchlist_hits, insert_watchlist_hits
from check_alerts_areas import get_area_hits, insert_area_hits
from counts import batch_statistics, grafana_today
from consume_alerts import kafka_consume

sys.path.append('../../common')
import settings

sys.path.append('../../common/src')
import date_nid, db_connect, manage_status, lasairLogging

def run_filter(args):

    if args['--topic_in']:
        topic_in = args['--topic_in']
    else:
        topic_in  = 'ztf_sherlock'

    if args['--group_id']:
        group_id = args['--group_id']
    else:
        group_id = settings.KAFKA_GROUPID

    if args['--maxalert']:
        maxalert = int(args['--maxalert'])
    else:
        maxalert = settings.KAFKA_MAXALERTS

    log = lasairLogging.getLogger("filter")
    log.info('Topic_in=%s, group_id=%s, maxalert=%d' % (topic_in, group_id, maxalert))

    ##### clear out the local database
    log.info('clear local caches')
    cmd = 'python3 refresh.py'
    if os.system(cmd) != 0:
        log.error("ERROR in filter/filter.py: refresh.py failed")
        sys.exit(0)
    
    ##### fetch a batch of annotated alerts
    log.info('FILTER start %s' % datetime.utcnow().strftime("%H:%M:%S"))
    log.info("Topic is %s" % topic_in)
    t = time.time()
    
    conf = {
        'bootstrap.servers'   : '%s' % settings.KAFKA_SERVER,
        'enable.auto.commit'  : False,   # require explicit commit!
        'group.id'            : group_id,
        'max.poll.interval.ms': 20*60*1000,  # 20 minute timeout in case queries take time
        'default.topic.config': { 'auto.offset.reset': 'smallest' }
    }
    log.info(str(conf))
    log.info('Topic in = %s' % topic_in)
    try:
        consumer = confluent_kafka.Consumer(conf)
        consumer.subscribe([topic_in])
    except Exception as e:
        log.error('ERROR cannot connect to kafka: %s' % str(e))
        return

    rc = kafka_consume(consumer, maxalert)

    # rc is the return code from ingestion, number of alerts received
    if rc < 0:
        log.error("ERROR in filter/filter: consume_kafka failed")
        sys.exit(0)
    
    log.info('FILTER duration %.1f seconds' % (time.time() - t))
    
    try:
        msl_local = db_connect.local()
    except:
        log.error('ERROR in filter/filter: cannot connect to local database')
        sys.exit(0)
    
    ##### run the watchlists
    log.info('WATCHLIST start %s' % datetime.utcnow().strftime("%H:%M:%S"))
    t = time.time()
    try:
        hits = get_watchlist_hits(msl_local, settings.WATCHLIST_MOCS, settings.WATCHLIST_CHUNK)
    except Exception as e:
        log.error("ERROR in filter/get_watchlist_hits: %s" % str(e))
        sys.exit(0)
    
    log.info('got %d watchlist hits' % len(hits))
    
    if len(hits) > 0:
        try:
            insert_watchlist_hits(msl_local, hits)
        except Exception as e:
            log.error("ERROR in filter/insert_watchlist_hits: %s" % str(e))
            sys.exit(0)
    
    log.info('WATCHLIST %.1f seconds' % (time.time() - t))
    
    ##### run the areas
    log.info('AREA start %s' % datetime.utcnow().strftime("%H:%M:%S"))
    t = time.time()
    try:
        hits = get_area_hits(msl_local, settings.AREA_MOCS)
    except Exception as e:
        log.error("ERROR in filter/get_area_hits: %s" % str(e))
        sys.exit(0)
    
    log.info('got %d area hits' % len(hits))
    if len(hits) > 0:
        try:
            insert_area_hits(msl_local, hits)
        except Exception as e:
            log.error("ERROR in filter/insert_area_hits: %s" % str(e))
            sys.exit(0)
    log.info('AREA %.1f seconds' % (time.time() - t))
    
    ##### run the user queries
    log.info('QUERIES start %s' % datetime.utcnow().strftime("%H:%M:%S"))
    t = time.time()
    try:
        query_list = run_active_queries.fetch_queries()
    except Exception as e:
        log.error("ERROR in filter/run_active_queries.fetch_queries: %s" % str(e))
        sys.exit(0)
    
    try:
        run_active_queries.run_queries(query_list)
    except Exception as e:
        log.error("ERROR in filter/run_active_queries.run_queries: %s" % str(e))
        sys.exit(0)
    log.info('QUERIES %.1f seconds' % (time.time() - t))
    
    ##### run the annotation queries
    log.info('ANNOTATION QUERIES start %s' % datetime.utcnow().strftime("%H:%M:%S"))
    t = time.time()
    try:
        run_active_queries.run_annotation_queries(query_list)
    except Exception as e:
        log.warning("WARNING in filter/run_active_queries.run_annotation_queries: %s" % str(e))
    log.info('ANNOTATION QUERIES %.1f seconds' % (time.time() - t))
    
    ##### build CSV file with local database
    t = time.time()
    log.info('SEND to ARCHIVE')
    cmd = 'sudo rm /data/mysql/*.txt'
    os.system(cmd)
    
    cmd = 'mysql --user=ztf --database=ztf --password=%s < output_csv.sql' % settings.LOCAL_DB_PASS
    if os.system(cmd) != 0:
        log.error('ERROR in filter/filter: cannot build CSV from local database')
        sys.exit(0)
    
    tablelist = ['objects', 'sherlock_classifications', 'watchlist_hits', 'area_hits']
    
    ##### send CSV file to central database
    t = time.time()

    #### if one of the tables doesn't go through, we run this batch again
    commit = True
    for table in tablelist:
        sql  = "LOAD DATA LOCAL INFILE '/data/mysql/%s.txt' " % table
        sql += "REPLACE INTO TABLE %s FIELDS TERMINATED BY ',' " % table
        sql += "ENCLOSED BY '\"' LINES TERMINATED BY '\n'"

        tmpfilename = tempfile.NamedTemporaryFile().name + '.sql'
        f = open(tmpfilename, 'w')
        f.write(sql)
        f.close()

        cmd =  "mysql --user=%s --database=ztf --password=%s --port=%s --host=%s < %s" 
        cmd = cmd % (settings.DB_USER_READWRITE, settings.DB_PASS_READWRITE, settings.DB_PORT, settings.DB_HOST, tmpfilename)
        if os.system(cmd) != 0:
            log.error('ERROR in filter/filter: cannot push %s local to main database' % table)
            commit = False
        else:
            log.info('%s table ingested to main db' % table)

    log.info('Transfer to main database %.1f seconds' % (time.time() - t))
    if commit:
        consumer.commit()
        consumer.close()
        log.info('Kafka committed for this batch')
    else:
        log.info('ERROR: No kafka commit')
        consumer.close()
        time.sleep(600)
        sys.exit(1)

    ms = manage_status.manage_status(settings.SYSTEM_STATUS)
    nid = date_nid.nid_now()
    d = batch_statistics()
    ms.set({
        'today_ztf':grafana_today(), 
        'today_database':d['count'], 
        'total_count': d['total_count'],
        'min_delay':d['min_delay'], 
        'nid': nid}, 
        nid)
    if rc > 0:
        t = int(1000*time.time())
        s  = 'lasair_alert_batch_lag{type="min"} %d %d\n' % (int(d['min_delay']*60), t)
        s += 'lasair_alert_batch_lag{type="avg"} %d %d\n' % (int(d['avg_delay']*60), t)
        s += 'lasair_alert_batch_lag{type="max"} %d %d\n' % (int(d['max_delay']*60), t)
        f = open('/var/lib/prometheus/node-exporter/lasair.prom', 'a')
        f.write(s)
        f.close()
        log.info('\n' + s)

    log.info('Return status %d' % rc)
    if rc > 0: return(1)
    else:      return(0)

if __name__ == '__main__':
    lasairLogging.basicConfig(stream=sys.stdout)
    log = lasairLogging.getLogger("filter")

    args = docopt(__doc__)
    # rc=1: got some alerts
    # rc=0: got no alerts

    rc = run_filter(args)
    sys.exit(rc)
