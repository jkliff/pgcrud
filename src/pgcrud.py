#!/usr/bin/env python
import sys
import json
import psycopg2
import psycopg2.extras
import yaml
import os

def __load_profile_def (profile):
    f = os.path.expanduser ('~/.pgcrud/profiles')

    if not os.path.exists (f):
        raise Exception ('Expected configuration file [%s] not expected.' % f)

    with (open (f)) as p:
        y = yaml.load (p)
        if profile not in y ['profiles']:
            raise Exception ('Requested profile [%s] not found in [%s]. ' % (profile, f))
        return y['profiles'][profile]

def __get_conn (conn_str):
    conn = psycopg2.connect (conn_str)
    return conn

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
        raise Exception ('PGCrud does not support this entity: either it has no pk or does not exists.')
    return pk [0]

def __split_data (data):

    cols = []
    vals = []
    for k, v in data.iteritems ():
        cols.append (k)
        vals.append (v)

    return cols, vals

def __default_sql_data_converter (obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

to_json = lambda x: json.dumps (x, default=__default_sql_data_converter)

def create (cur, entity, data):

    cols, vals = __split_data (data)
    pk = __get_pk (cur, entity)

    sql = """insert into %s (%s) values (%s)
returning %s;""" % (
        entity,
        ', '.join (cols),
        ', '.join (["""'%s'""" % x for x in vals]),
        pk
    )
    cur.execute (sql)
    r = cur.fetchone ()
    return r [pk]

def retrieve (cur, entity, data):

    pk = __get_pk (cur, entity)

    sql = """select *
from %(table_name)s
where %(pk_name)s = %(id)s;
""" % {
        'table_name': entity,
        'pk_name': pk,
        'id': data
    }

    cur.execute (sql)
    r = cur.fetchone ()
    return to_json(dict (r.items()))

def retrieve_all (cur, entity, data):

    sql = """select *
from %(table_name)s
""" % {
        'table_name': entity,
    }

    cur.execute (sql)
    r = cur.fetchall ()

    return to_json([dict (i) for i in r])


def update (cur, entity, data):
    """__ is the identifier of the id"""

    pk = __get_pk (cur, entity)

    sql = """update %(table_name)s
set %(update_cols)s
where %(pk_name)s = %(id)s;
""" % {
        'table_name': entity,
        'pk_name': pk,
        'id': data ['__'],
        'update_cols': ', '.join (["%s = '%s'" % (x, data [x]) for x in data.iterkeys() if x != '__'])
    }

    cur.execute (sql)

def delete (cur, entity, data):
    pk = __get_pk (cur, entity)

    sql = """delete from %(table_name)s
where %(pk_name)s = %(id)s;
""" % {
        'table_name': entity,
        'pk_name': pk,
        'id': data
    }

    cur.execute (sql)
    #r = cur.fetchone ()

def main (argv):

    CMDS = {
        'create':   create,
        'retrieve': retrieve,
        'update':   update,
        'delete':   delete,
        'list':     retrieve_all
    }


    if len (argv) < 4:
        print 'Not enough arguments. Check your call.'
        return -2

    profile = argv [1]
    method = argv [2]
    entity = argv [3]
    data = None
    if method != 'list':
        data = json.loads (argv [4])

    try:
        conn = __get_conn (__load_profile_def (profile))
    except Exception as e:
        print e
        print 'Aborting'
        return -10

    cur = conn.cursor (cursor_factory=psycopg2.extras.DictCursor)

    r = CMDS [method] (cur, entity, data)
    if r is not None:
        print r

    conn.commit ()
    cur.close ()
    conn.close ()

    return 0

if __name__ == '__main__':
    sys.exit (main(sys.argv))
