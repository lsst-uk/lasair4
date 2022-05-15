"""Check Object Database Schema
Validate the schema used in the object database against the JSON version of the schema in git.
Raises an AssertionError and returns with non-zero if the number of fields or names of fields
differ (types are not checked).
"""

import sys
sys.path.append('../common')
from src import db_connect
import importlib

def get_mysql_attrs():
    msl = db_connect.readonly()

    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'describe objects'
    cursor.execute(query)
    mysql_attrs = []
    for row in cursor:
        mysql_attrs.append(row['Field'])
    return mysql_attrs

if __name__ == "__main__":
    if len(sys.argv) > 1:
        schema_name = sys.argv[1]
    else:
        print('Usage: python check_schema.py schema_name')
        sys.exit()

    schema_attrs = []
    schema_package = importlib.import_module('schema.' + schema_name)
    schema = schema_package.schema
    for field in schema['fields']:
        schema_attrs.append(field['name'])

    mysql_attrs = get_mysql_attrs()

    assert len(mysql_attrs) == len(schema_attrs), "Schema validation failed: different length"

    for i in range(len(mysql_attrs)):
        assert mysql_attrs[i] == schema_attrs[i], "Schema validation failed: {} != {}".format(mysql_attrs[i], schema_attrs[i])

    print('mysql and object schema identical')
