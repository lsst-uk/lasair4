"""
Ingestion code for Lasair. Takes a stream of AVRO, splits it into
FITS cutouts to Ceph, Lightcurves to Cassandra, and JSON versions of 
the AVRO packets, but without the cutouts, to Kafka.
Usage:
    ingest.py [--maxalert=MAX]
              [--group_id=GID]
              [--topic_in=TIN | --nid=NID] 
              [--topic_out=TOUT]

Options:
    --maxalert=MAX     Number of alerts to process, default is infinite
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
from src import objectStore, date_nid
from src.manage_status import manage_status
from confluent_kafka import Consumer, Producer, KafkaError
from gkhtm import _gkhtm as htmCircle
from cassandra.cluster import Cluster
from gkdbutils.ingesters.cassandra import executeLoad
import os, time, json, zlib, signal, io, fastavro

sigterm_raised = False

def sigterm_handler(signum, frame):
    global sigterm_raised
    sigterm_raised = True
    print("Caught SIGTERM")

signal.signal(signal.SIGTERM, sigterm_handler)

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
    try:
        for cutoutType in ['cutoutDifference', 'cutoutTemplate', 'cutoutScience']:
            contentgz = message[cutoutType]['stampData']
            content = zlib.decompress(contentgz, 16+zlib.MAX_WBITS)
            filename = '%d_%s' % (candid, cutoutType)
            store.putObject(filename, content)
        return 0
    except Exception as e:
        print(e)
        return None # failure of batch

def insert_cassandra(alert, cassandra_session):
    """insert_casssandra.
    Creates an insert for cassandra
    a query for inserting it.

    Args:
        alert:
    """

    # if this is not set, then we are not doing cassandra
    if not cassandra_session:
        return None   # failure of batch

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
        cassandra_session
    """
    # here is the part of the alert that has no binary images
    alert_noimages = msg_text(alert)
    candid = alert_noimages['candidate']['candid']
    objectId = alert_noimages['objectId']

    if not alert_noimages:
        print('ERROR: in ingest.py: No json in alert')
        return None  # ingest batch failed

    # candidates to cassandra
    try:
        ncandidate = insert_cassandra(alert_noimages, cassandra_session)
    except:
        print('ERROR: in ingest.py: Cassandra insert failed')
        return None  # ingest batch failed

    # store the fits images
    if image_store:
        if store_images(alert, image_store, candid) == None:
            print('ERROR: in ingest.py: Failed to put cutouts in file system')
            return None   # ingest batch failed

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
            return None   # ingest failed
    return ncandidate

def main(args):
    """main.
    """
    global sigterm_raised

    if args['--topic_in']:
        topic_in = args['--topic_in']
    elif args['--nid']:
        nid = int(args['--nid'])
        date = date_nid.nid_to_date(nid)
        topic_in  = 'ztf_' + date + '_programid1'
    else:
        # get all alerts from every nid
        topic_in = '^ztf_202211.*_programid1$'

    if args['--topic_out']:
        topic_out = args['--topic_out']
    else:
        topic_out = 'ztf_ingest'

    if args['--group_id']:
        group_id = args['--group_id']
    else:
        group_id = settings.KAFKA_GROUPID

    if args['--maxalert']:
        maxalert = int(args['--maxalert'])
    else:
        maxalert = sys.maxsize  # largest possible integer

    try:
        fitsdir = settings.IMAGEFITS
    except:
        fitsdir = None

    # set up image store in shared file system
    if fitsdir and len(fitsdir) > 0:
        image_store  = objectStore.objectStore(suffix='fits', fileroot=fitsdir)
    else:
        print('ERROR in ingest/ingestBatch: No image directory found for file storage')
        sys.stdout.flush()
        image_store = None

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

    # set up kafka consumer
    print('Consuming from %s' % settings.KAFKA_SERVER)
    print('Topic_in       %s' % topic_in)
    print('Topic_out      %s' % topic_out)
    print('group_id       %s' % group_id)
    print('maxalert       %d' % maxalert)

    consumer_conf = {
        'bootstrap.servers'   : '%s' % settings.KAFKA_SERVER,
        'group.id'            : group_id,
        'enable.auto.commit'  : False,
        'max.poll.interval.ms': 20*60*1000,  # wait 20 min before forgetting me
        'session.timeout.ms'  : 6000,
        'default.topic.config': {'auto.offset.reset': 'smallest'}
    }

    try:
        consumer = Consumer(consumer_conf)
    except:
        print('ERROR in ingest/ingestBatch: Cannot connect to Kafka')
        sys.stdout.flush()
        return 1
    consumer.subscribe([topic_in])

    # set up kafka producer
    producer_conf = {
        'bootstrap.servers': '%s' % settings.KAFKA_SERVER,
        'client.id': 'client-1',
    }
    producer = Producer(producer_conf)
    print('Producing to   %s' % settings.KAFKA_SERVER)

    nalert = 0        # number not yet send to manage_status
    ncandidate = 0    # number not yet send to manage_status
    ntotalalert = 0   # number since this program started
    print('INGEST starts', now())

    # put status on Lasair web page
    ms = manage_status(settings.SYSTEM_STATUS)

    while ntotalalert < maxalert:

        msg = consumer.poll(timeout=5)

        # no messages available
        if msg is None:
            end_batch(consumer, producer, ms, nalert, ncandidate)
            nalert = ncandidate = 0
            print('no more messages ... sleeping')
            sys.stdout.flush()
            time.sleep(600) # sleep 10 minutes
            continue

        # read the avro contents
        try:
            bytes_io = io.BytesIO(msg.value())
            msg = fastavro.reader(bytes_io)
        except:
            print(msg.value())
            break

        for alert in msg:
            if sigterm_raised:
                # clean shutdown - this should stop the consumer and commit offsets
                print("Stopping ingest")
                sys.stdout.flush()
                break

            # Apply filter to each alert
            icandidate = handle_alert(alert, image_store, producer, topic_out, cassandra_session)

            if icandidate == None:
                print('Ingestion failed ')
                return 0

            nalert += 1
            ntotalalert += 1
            ncandidate += icandidate

            # every so often commit, flush, and update status
            if nalert >= 5000:
                end_batch(consumer, producer, ms, nalert, ncandidate)
                nalert = ncandidate = 0

        if sigterm_raised:  # need to break out of two loops if sigterm
            break

    # if we exit this loop, clean up
    print('Shutting down')
    end_batch(consumer, producer, ms, nalert, ncandidate)

    # shut down kafka consumer
    consumer.close()

    # shut down the cassandra cluster
    if cassandra_session:
        cluster.shutdown()

    # did we get any alerts
    if ntotalalert > 0: return 1
    else:               return 0

def end_batch(consumer, producer, ms, nalert, ncandidate):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")
    print('%s %d alerts %d candidates' % (date, nalert, ncandidate))
    # if this is not flushed, it will run out of memory
    if producer is not None:
        producer.flush()

    # commit the alerts we have read
    consumer.commit()
    sys.stdout.flush()

    # update the status page
    nid  = date_nid.nid_now()
    ms.add({'today_alert':nalert, 'today_candidate':ncandidate}, nid)

if __name__ == "__main__":
    args = docopt(__doc__)
    rc = main(args)
    # rc=1, got alerts, more to come
    # rc=0, got no alerts
    sys.exit(rc)
