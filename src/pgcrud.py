#!env python
import sys
import json
import psycopg2
import psycopg2.extras
import yaml
import os

def create (cur, entity, data):

    cols = []
    vals = []
    for k, v in data.iteritems ():
        cols.append (k)
        vals.append (v)

    sql = """insert into %s (%s) values (%s);""" % (
        entity,
        ', '.join (cols),
        ', '.join (["""'%s'""" % x for x in vals])
    )
    cur.execute (sql)

def retrieve (cur, entity, data, pk=__get_pk (cur, entity)):
    sql = """select *
from %(table_name)s
where %(pk_name)s = %(id)s;""" % {'table_name': entity, 'pk_name': pk, 'id': data}

    cur.execute (sql)
    r = cur.fetchone ()
    print json.dumps (dict (r.items()))

def update (cur, entity, data):
    pass

def delete (cur, entity, data):
    pass

def __get_pk (cur, table):
    sql = """select attname
from pg_catalog.pg_class
    join pg_catalog.pg_attribute on attrelid = pg_class.oid and attnum > 0
    join pg_constraint on conrelid = pg_class.oid and attnum = any (conkey)
where relname = %(table_name)s
    and contype = 'p';
"""
    cur.execute (sql, {'table_name': table})
    pk = cur.fetchone ()
    if pk is None:
        raise Exception ('either entity has no pk or does not exists.')
    return pk [0]

CMDS = {
    'create':   create,
    'retrieve': retrieve,
    'update':   update,
    'delete':   delete
}

def load_profile_def (profile):
    with (open (os.path.expanduser ('~/.pgcrud/profiles'))) as p:
        y = yaml.load (p)
        return y['profiles'][profile]

def get_conn (conn_str):
    conn = psycopg2.connect (conn_str)
    return conn

def main (argv):

    profile = argv [1]
    method = argv [2]
    entity = argv [3]
    data = json.loads (argv [4])

    conn = get_conn (load_profile_def (profile))
    cur = conn.cursor (cursor_factory=psycopg2.extras.DictCursor)
    CMDS [method] (cur, entity, data)
    conn.commit ()
    cur.close ()
    conn.close ()

    return 0

if __name__ == '__main__':
    sys.exit (main(sys.argv))
