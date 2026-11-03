"""Print MySQL DDL for the Lasair raw-SQL tables.

Uses `create_table()` from `common/schema/convert.py`, the same generator that
made the committed `common/schema/*.sql` files, without writing into that folder.
"""
import importlib
import os
import sys

SCHEMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'common', 'schema')
TABLES = ('objects', 'sherlock_classifications', 'watchlist_hits', 'area_hits',
          'crossmatch_tns', 'annotations')


def main():
    sys.path.insert(0, os.path.abspath(SCHEMA_DIR))
    from convert import create_table
    for table in TABLES:
        print(create_table(importlib.import_module(table).schema) + ';\n')


if __name__ == '__main__':
    main()
