"""
This program reads avro files as published by ZTF in 
https://caltech.box.com/s/09wdqwg3xv6kitq4k8na5qn01gw62pxc

Each alert is then written into a kafka server, without schema.
"""
from confluent_kafka import Producer, KafkaError
import fastavro
import json, sys, os

# where we downloaded the files
dir = '/mnt/cephfs/forcedphot'

# the kafka server where the alerts will go
KAFKA = 'lasair-dev-kafka-0'

conf = {
    'bootstrap.servers': KAFKA,
    'client.id': 'client-1',
}
p = Producer(conf)

topic='forcedphot_schema'

nalert = 0
for filename in os.listdir(dir):
    f = open(dir+'/'+filename,'rb')
    alert = f.read()
    p.produce(topic, alert)
    p.flush()
    nalert += 1
    if nalert%1000 == 0:
         print('.', end='', flush=True)

print('%d alerts in topic %s' % (nalert,  topic))
