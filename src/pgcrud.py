#!env python
import sys
import json
import psycopg2

def create (conn, entity, data):
    pass

def retrieve (conn, entity, data):
    pass

def update (conn, entity, data):
    pass

def delete (conn, entity, data):
    pass


CMDS = {
    'create':   create,
    'retrieve': retrieve,
    'update':   update,
    'delete':   delete
}

def get_conn (profile):
    pass


def main (argv):

    profile = argv [1]
    method = argv [2]
    entity = argv [3]
    data = json.loads (argv [4])

    with (get_conn (profile)) as conn:
        CMDS [method] (conn, entity, data)

    return 0

if __name__ == '__main__':
    sys.exit (main(sys.argv))
