# file comes from 
# https://github.com/ZwickyTransientFacility/ztf-avro-alert/blob/master/schema/fp_hist.avsc
import json
fp = json.loads(open('fp_hist.avsc').read())

print('CREATE TABLE IF NOT EXISTS forcedphot(')

# objectId is not in schema, will come from the parent alert
print('  objectid ascii,')

for a in fp['fields']:
    t = a['type']

    if type(t) is list: t = t[1]
    if t == 'string':   t = 'ascii'
    if t == 'long':     t = 'bigint'

    print('  %s %s,' % (a['name'], t))
print('  PRIMARY KEY (objectid, jd)')
print(')')
