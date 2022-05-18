import os, sys
sys.path.append('../../../common')
from fink_client.consumer import AlertConsumer
import random
from datetime import datetime
import lasair
import settings

# Lasair client
L = lasair.lasair_client(settings.API_TOKEN)
topic_out = 'fink_early_sn'

# Fink configuration
fink_config = {
    'username':          settings.FINK_USERNAME ,
    'bootstrap.servers': settings.FINK_SERVERS,
    'group_id':          settings.FINK_GROUP_ID
}

# Instantiate a consumer
consumer = AlertConsumer(settings.FINK_TOPICS, fink_config)

nalert = 0
maxtimeout = 5
while 1:
    (topic, alert, version) = consumer.poll(maxtimeout)
    if topic is None:
        break

    objectId = alert['objectId']
    classification = 'early_sn'
    try:
        classdict = {
            'rfcsore':           float(alert['rfscore']), 
            'snn_snia_vs_nonia': float(alert['snn_snia_vs_nonia']), 
            'snn_sn_vs_all':     float(alert['snn_sn_vs_all']), 
            'knscore':           float(alert['knscore']),
        }
    except:
        continue

    L.annotate(
        topic_out,
        objectId,
        classification,
        version='0.1',
        explanation='',
        classdict=classdict,
        url='')

    nalert += 1
if nalert > 0:
    print('\n-- %d from Fink at %s' % (nalert, datetime.now()))
