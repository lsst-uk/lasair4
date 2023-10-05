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

topic='forcedphot'
tmpfile = 'tmp.avro'

nalert = 0
for filename in os.listdir(dir):
    f = open(dir+'/'+filename,'rb')
    freader = fastavro.reader(f)
    schema = freader.writer_schema
#    print(json.dumps(schema, indent=2))
    parsed_schema = fastavro.parse_schema(schema)

    for packet in freader:
        tmp = open(tmpfile, 'wb')
        fastavro.schemaless_writer(tmp, parsed_schema, packet)
        tmp.close()
        tmp = open(tmpfile, 'rb')
        alert = tmp.read()
        tmp.close()
        os.system('ls -l tmp.avro')
        if len(alert) > 1000000:  # dump the giant cutouts
            continue
        p.produce(topic, alert)
        p.flush()
        nalert += 1
        if nalert%1000 == 0:
             print('.', end='', flush=True)

print('%d alerts in topic %s' % (nalert,  topic))
