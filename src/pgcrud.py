#!env python
import sys
import json
import psycopg2
import yaml
import os

def create (cur, entity, data):
    pass

def retrieve (cur, entity, data):
    pass

def update (cur, entity, data):
    pass

def delete (cur, entity, data):
    pass


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
    cur = conn.cursor ()
    CMDS [method] (cur, entity, data)
    cur.close ()
    conn.close ()

    return 0

if __name__ == '__main__':
    sys.exit (main(sys.argv))
