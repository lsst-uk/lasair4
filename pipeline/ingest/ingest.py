"""
Ingestion code for Lasair. Takes a stream of AVRO, splits it into
FITS cutouts to Ceph, Lightcurves to Cassandra, and JSON versions of 
the AVRO packets, but without the cutouts, to Kafka.
Usage:
    ingest.py [--nprocess=NPROCESS] 
              [--maxalert=MAX]
              [--group_id=GID]
              [--topic_in=TIN | --nid=NID] 
              [--topic_out=TOUT]

Options:
    --nprocess=NP      Number of processes to use [default:1]
    --maxalert=MAX     Number of alerts to process, default is from settings.
    --group_id=GID     Group ID for kafka, default is from settings
    --topic_in=TIN     Kafka topic to use, or
    --nid=NID          ZTF night number to use (default today)
    --topic_out=TOUT   Kafka topic for output [default:ztf_sherlock]
"""

import sys
sys.path.append('../../common')
import settings
from docopt import docopt
from datetime import datetime
from multiprocessing import Process, Manager
import alertConsumer
from src import objectStore, date_nid
from src.manage_status import manage_status
from confluent_kafka import Producer, KafkaError
from gkhtm import _gkhtm as htmCircle
from cassandra.cluster import Cluster
from gkdbutils.ingesters.cassandra import executeLoad
import os, time, json, zlib

def now():
    # current UTC as string
    return datetime.utcnow().strftime("%Y/%m/%dT%H:%M:%S")

def msg_text(message):
    """msg_text. Remove postage stamp cutouts from an alert message.

    Args:
        message:
    """
    message_text = {k: message[k] for k in message
                    if k not in ['cutoutDifference', 'cutoutTemplate', 'cutoutScience']}
    return message_text

def store_images(message, store, candid):
    for cutoutType in ['cutoutDifference', 'cutoutTemplate', 'cutoutScience']:
        contentgz = message[cutoutType]['stampData']
        content = zlib.decompress(contentgz, 16+zlib.MAX_WBITS)
        filename = '%d_%s' % (candid, cutoutType)
        store.putObject(filename, content)

def insert_cassandra(alert, cassandra_session):
    """insert_casssandra.
    Creates an insert for cassandra
    a query for inserting it.

    Args:
        alert:
    """

    # if this is not set, then we are not doing cassandra
    if not cassandra_session:
        return 0

    # if it does not have all the ZTF attributes, don't try to ingest
    if not 'candid' in alert['candidate'] or not alert['candidate']['candid']:
        return 0

    objectId =  alert['objectId']

    candlist = None
    # Make a list of candidates and noncandidates in time order
    if 'candidate' in alert and alert['candidate'] != None:
        if 'prv_candidates' in alert and alert['prv_candidates'] != None:
            candlist = alert['prv_candidates'] + [alert['candidate']]
        else:
            candlist = [alert['candidate']]

    # will be list of real detections, each has a non-null candid
    detectionCandlist = []
    nondetectionCandlist = []

    # 2021-03-01 KWS Issue 134: Add non detections.
    for cand in candlist:
        cand['objectId'] = objectId
        if not 'candid' in cand or not cand['candid']:
            # This is a non-detection. Just append the subset of attributes we want to keep.
            # The generic cassandra inserter should be able to insert correctly based on this.
            nondetectionCandlist.append({'objectId': cand['objectId'],
                                         'jd': cand['jd'],
                                         'fid': cand['fid'],
                                         'diffmaglim': cand['diffmaglim'],
                                         'nid': cand['nid'],
                                         'field': cand['field'],
                                         'magzpsci': cand['magzpsci'],
                                         'magzpsciunc': cand['magzpsciunc'],
                                         'magzpscirms': cand['magzpscirms']})
        else:
            detectionCandlist.append(cand)

    if len(detectionCandlist) == 0 and len(nondetectionCandlist) == 0:
        # No point continuing. We have no data.
        return 0

    if len(detectionCandlist) > 0:
        # Add the htm16 IDs in bulk. Could have done it above as we iterate through the candidates,
        # but the new C++ bulk code is 100 times faster than doing it one at a time.
        # Note that although we are inserting them into cassandra, we are NOT using
        # HTM indexing inside Cassandra. Hence this is a redundant column.
        htm16s = htmCircle.htmIDBulk(16, [[x['ra'],x['dec']] for x in detectionCandlist])

        # Now add the htmid16 value into each dict.
        for i in range(len(detectionCandlist)):
            detectionCandlist[i]['htmid16'] = htm16s[i]

        executeLoad(cassandra_session, settings.CASSANDRA_CANDIDATES, detectionCandlist)

    if len(nondetectionCandlist) > 0:
        executeLoad(cassandra_session, settings.CASSANDRA_NONCANDIDATES, nondetectionCandlist)

    return len(detectionCandlist)

def handle_alert(alert, image_store, producer, topic_out, cassandra_session):
    """handle_alert.
    Filter to apply to each alert.
       See schemas: https://github.com/ZwickyTransientFacility/ztf-avro-alert

    Args:
        alert:
        image_store:
        producer:
        topic_out:
    """
    # here is the part of the alert that has no binary images
    alert_noimages = msg_text(alert)
    if not alert_noimages:
        return None

    # Call on Cassandra
    if cassandra_session:
        ncandidate = insert_cassandra(alert_noimages, cassandra_session)
    else:
        ncandidate = 0

    # add to CephFS
    candid = alert_noimages['candidate']['candid']
    objectId = alert_noimages['objectId']

    # store the fits images
    if image_store:
        store_images(alert, image_store, candid)

    # do not put known solar system objects into kafka
#    ss_mag = alert_noimages['candidate']['ssmagnr']
#    if ss_mag > 0:
#        return None

        # produce to kafka
    if producer is not None:
        try:
            s = json.dumps(alert_noimages)
            producer.produce(topic_out, json.dumps(alert_noimages))
        except Exception as e:
            print("ERROR in ingest/ingestBatch: Kafka production failed for %s" % topic_out)
            print(e)
            sys.stdout.flush()
    return ncandidate

def run(runarg, return_dict):
    """run.
    """
    processID = runarg['processID']

    # connect to cassandra cluster
    try:
        cluster = Cluster(settings.CASSANDRA_HEAD)
        cassandra_session = cluster.connect()
        cassandra_session.set_keyspace('lasair')
    except Exception as e:
        print("ERROR in ingest/ingestBatch: Cannot connect to Cassandra")
        sys.stdout.flush()
        cassandra_session = None
        print(e)

    try:
        streamReader = alertConsumer.AlertConsumer(runarg['topic'], **runarg['consumer_conf'])
        streamReader.__enter__()
    except alertConsumer.EopError as e:
        print('ERROR in ingest/ingestBatch: Cannot connect to Kafka')
        sys.stdout.flush()
        return

    topic_out = runarg['topic_out']
    producer_conf = {
        'bootstrap.servers': '%s' % settings.KAFKA_SERVER,
#        'group.id': 'copy-topic',
        'client.id': 'client-1',
#        'enable.auto.commit': True,
#        'session.timeout.ms': 6000,
#        'default.topic.config': {'auto.offset.reset': 'smallest'}
    }
    producer = Producer(producer_conf)
    print('Producing Kafka to %s with topic %s' % (settings.KAFKA_SERVER, topic_out))

    if runarg['maxalert']:
        maxalert = runarg['maxalert']
    else:
        maxalert = 50000

    nalert = 0
    ncandidate = 0
    startt = time.time()
    while nalert < maxalert:
        t = time.time()
        try:
            msg = streamReader.poll(decode=True, timeout=5)
        except alertConsumer.EopError as e:
            print('eop end of messages')
            sys.stdout.flush()
            break

        if msg is None:
            print('null message end of messages')
            sys.stdout.flush()
            break
        else:
            for alert in msg:
                # Apply filter to each alert
                icandidate = handle_alert(alert, runarg['image_store'], \
                        producer, topic_out, cassandra_session)

                nalert += 1
                ncandidate += icandidate

                if nalert%1000 == 0:
                    print('process %d nalert %d time %.1f' % \
                            ((processID, nalert, time.time()-startt)))
                    sys.stdout.flush()
                    # if this is not flushed, it will run out of memory
                    if producer is not None:
                        producer.flush()
    # finally flush
    if producer is not None:
        producer.flush()

    print('INGEST %d finished with %d alerts %d candidates' \
            % (processID, nalert, ncandidate))
    sys.stdout.flush()
    streamReader.__exit__(0,0,0)

    # shut down the cassandra cluster
    if cassandra_session:
        cluster.shutdown()

    return_dict[processID] = { 'nalert':nalert, 'ncandidate': ncandidate }

def main(args):
    """main.
    """

    if args['--topic_in']:
        topic_in = args['--topic_in']
    elif args['--nid']:
        nid = int(args['--nid'])
        date = date_nid.nid_to_date(nid)
        topic  = 'ztf_' + date + '_programid1'
    else:
        nid  = date_nid.nid_now()
        date = date_nid.nid_to_date(nid)
        topic  = 'ztf_' + date + '_programid1'

    if args['--nprocess']:
        nprocess = int(args['--nprocess'])
    else:
        nprocess = 1

    if args['--topic_out']:
        topic_out = args['--topic_out']
    else:
        topic_out = 'ztf_sherlock'

    if args['--group_id']:
        group_id = args['--group_id']
    else:
        group_id = settings.KAFKA_GROUPID

    if args['--maxalert']:
        maxalert = int(args['--maxalert'])
    else:
        maxalert = settings.KAFKA_MAXALERTS
    

    print('Topic_in=%s, topic_out=%s, group_id=%s, nprocess=%d, maxalert=%d' % (topic, topic_out, group_id, nprocess, maxalert))

    try:
        fitsdir = settings.IMAGEFITS
    except:
        fitsdir = None

    print('INGEST ----------', now())

    consumer_conf = {
        'bootstrap.servers': '%s' % settings.KAFKA_SERVER,
        'group.id': group_id,
        'enable.auto.commit': True,
        'session.timeout.ms': 6000,
        'default.topic.config': {'auto.offset.reset': 'smallest'}
    }

    if fitsdir and len(fitsdir) > 0:
        image_store  = objectStore.objectStore(suffix='fits', fileroot=fitsdir)
    else:
        print('ERROR in ingest/ingestBatch: No image directory found for file storage')
        sys.stdout.flush()
        image_store = None

#    print('Configuration = %s' % str(conf))

    print('Processes = %d' % nprocess)
    sys.stdout.flush()

    runargs = []
    process_list = []
    manager = Manager()
    return_dict = manager.dict()
    t = time.time()
    for t in range(nprocess):
        runarg = {
            'processID':t, 
            'topic'   : topic,
            'maxalert'   : maxalert,
            'topic_out':topic_out,
            'image_store': image_store,
            'consumer_conf':consumer_conf,
        }
        p = Process(target=run, args=(runarg, return_dict))
        process_list.append(p)
        p.start()

    for p in process_list:
        p.join()

    r = return_dict.values()
    nalert = ncandidate = 0
    for t in range(nprocess):
        nalert     += r[t]['nalert']
        ncandidate += r[t]['ncandidate']
    print('%d alerts and %d candidates' % (nalert, ncandidate))
    sys.stdout.flush()

    os.system('date')
    ms = manage_status(settings.SYSTEM_STATUS)
    nid  = date_nid.nid_now()
    ms.add({'today_alert':nalert, 'today_candidate':ncandidate}, nid)

    if nalert > 0: return 1
    else:          return 0

if __name__ == "__main__":
    args = docopt(__doc__)
    rc = main(args)
    sys.exit(rc)
