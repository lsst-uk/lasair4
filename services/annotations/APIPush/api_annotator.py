# This code shows how to read a stream from Lasair, 
# extract the lightcurve and Sherlock information,
# and push annotations back into Lasair
# will need to pip install lasair
# will need to pip install confluent_kafka

import json, sys
import lasair
import settings
import random

# This function deals with an object once it is received from Lasair
def handle_object(objectId, L, topic_out):
    # from the objectId, we can get all the info that Lasair has
    objectInfo = L.objects([objectId])[0]
    if not objectInfo:
        return 0

#    print('----------------------------------')
    # here is the lightcurve. Note that fid=1 from g band, fid=2 for r band
#    print(objectId, 'Lightcurve')
#    for cand in objectInfo['candidates']:
#        if 'candid' in cand:
#            print(cand['jd'], cand['fid'], cand['magpsf'])

    # here is all the info from Sherlock
#    print(objectId, 'Sherlock')
#    print(json.dumps(objectInfo['sherlock'], indent=2))

    # the classification is just a dummy!
    # put in some real code here! 
    if random.random() > 0.3:
        print(objectId, '-- not annotated')
        return 0

    ncand = objectInfo['objectData']['ncand']
    classdict      = {'ncand': ncand}

    if ncand < 20:
        classification = 'few'
        explanation    = 'not many candidates'
    else:
        classification = 'many'
        explanation    = 'lots of candidates'

    # now we annotate the Lasair data with the classification
    L.annotate(
        topic_out, 
        objectId, 
        classification,
        version='0.1', 
        explanation=explanation, 
        classdict=classdict, 
        url='')
    print(objectId, '-- annotated!')
    return 1

#####################################
# first we set up pulling the stream from Lasair
# use a new group_id each time
group_id = 'g%d' % random.randrange(10000)

# this corresponds to a query-stream from Lasair
# see https://lasair-iris.roe.ac.uk/query/2/
# and https://lasair-iris.roe.ac.uk/streams/lasair_2SN-likecandidates/
topic_in = 'lasair_2SN-likecandidates'

# this is the kafka consumer that we can suck from
consumer = lasair.lasair_consumer('kafka.lsst.ac.uk:9092', group_id, topic_in)

# the lasair client will be used for pulling all the info about the object
# and for annotating it
# Note: topic_out must be owned by the perso whose token this is
L = lasair.lasair_client(settings.API_TOKEN, endpoint='https://lasair-dev.lsst.ac.uk/api')
#L = lasair.lasair_client(settings.API_TOKEN)
topic_out = 'test'

# just get a few to start
max_alert = 10
selected    = 'objects.objectId, ramean, decmean'
tables      = 'objects, sherlock_classifications'
conditions  = 'sherlock_classifications.classification = "SN"'
objects = L.query(selected, tables, conditions, limit=10, offset=20)
print(objects)

n_alert = 0
n_annotate = 0
for o in objects:
    objectId = o['objectId']
    print(objectId)
    n_annotate += handle_object(objectId, L, topic_out)
    n_alert += 1
print('Read %d alerts, and annotated %d of them' % (n_alert, n_annotate))

