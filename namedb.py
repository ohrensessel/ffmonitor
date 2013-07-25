from configuration import config
import logging
import atexit
import json


logger = logging.getLogger('monitor')

# name dictonary
name_db = {}


def _write_name_db():
# writes the name database to disk

    try:
        with open(config.get('data', 'namedb'), 'w') as fp:
            # json instead of pickle is used here
            # to allow reading from php
            json.dump(name_db, fp)

    except Exception:
        logger.error('could not write name database to: %s',
                     config.get('data', 'namedb'))


def get_name(clean_id):
    """returns the name associated with the given id

    Arguments:
    clean_id -- a node id without colons

    """
    if clean_id in name_db:
        return name_db['clean_id']

    else:
        return ':'.join(clean_id[i:i+2] for i in xrange(0, len(clean_id), 2))

def save_name(clean_id, name):
    """saves a id to name association in the database

    Arguments:
    clean_id -- a node id without colons
    name -- the associated name
        
    """
    # empty names are disregarded
    if len(name) == 0:
        return

    global name_db
    name_db[clean_id] = name


def init_read():
    """initializes the database for reading only"""
    try:
        with open(config.get('data', 'namedb'), 'r') as fp:
            global name_db
            name_db = json.load(fp)

    except Exception:
        logger.warning('could not load name database from: %s',
                       config.get('data', 'namedb'))


def init():
    """initializes the database for reading and writing"""
    init_read()

    # database should be written on program termination
    atexit.register(_write_name_db)

