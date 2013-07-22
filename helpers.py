#!/usr/bin/python
from __future__ import print_function
import os.path
import requests
import time
from functools import wraps
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import email.utils
import rrdtool
import atexit
import json
import ConfigParser 
import retry\\-decorator.decorators

config = ConfigParser.RawConfigParser();
config.read('monitoring.conf')

daemon = config.get('rrd', 'daemon')
rrd_path = config.get('rrd', 'path')
file_last_modified = config.get('data', 'lastmodified')
data_url = config.get('data', 'url') 

handler = logging.FileHandler('helpers.log', 'a')
format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(format)

logger = logging.getLogger()
logger.addHandler(handler)



@retry(Exception, tries=4)
def getFFData():
    
    headers = {}
    modifiedSince = ''
    eTag = ''
            
    try:
        with open(fileLastModified, 'r') as fp:
            modifiedSince = fp.readline().rstrip('\n')
            eTag = fp.readline().rstrip('\n')
    except IOError:
        print('file not found ', fileLastModified)
    except Exception:
        print('could not read data from file')
    else:
        if len(modifiedSince) > 0:
            headers['If-Modified-Since'] = modifiedSince
        if len(eTag) > 0:
            headers['If-None-Match'] = eTag

    r = requests.get(nodeDataUrl, headers=headers, timeout=6)
    r.raise_for_status()

    if r.status_code == 304:
        raise Exception('node list not modified')
    elif r.status_code == 200:
        try:
            with open(fileLastModified, 'w') as fp:
                if not r.headers['Last-Modified'] is None:
                    print(r.headers['Last-Modified'], file=fp)
                else:
                    now = datetime.now()
                    stamp = mktime(now.timetuple())
                    print(format_date_time(stamp),file=fp)
                if not r.headers['ETag'] is None:
                    print(r.headers['ETag'], file=fp)
                else:
                    print('', file=fp)
        except Exception:
            print('could not write to file')

        global dataDate
        if not r.headers['Last-Modified'] is None:
            dataDate = str(int(email.utils.mktime_tz(email.utils.parsedate_tz(r.headers['Last-Modified']))))
            print('file ', dataDate)
        else:
            dataDate = str(int(time.time()))
            print('gen ', dataDate)
        
        dataDate = str(dataDate)

        return r.text
    else:
        raise Exception('unexpected status code')

# data source for nodes
dsNodes = [     "DS:clients:GAUGE:120:0:32768",
        "DS:wifilinks:GAUGE:120:0:32768",
        "DS:vpns:GAUGE:120:0:32768" ]

# data source for total numbers
dsTotal = [     "DS:nodes:GAUGE:120:0:32768",
        "DS:clients:GAUGE:120:0:32768",
        "DS:gateways:GAUGE:120:0:32768",
        "DS:nodesoffline:GAUGE:120:0:32768",
        "DS:nodesgeo:GAUGE:120:0:32768",
        "DS:nodesoffgeo:GAUGE:120:0:32768" ]

# save data to rrd files
def updateRRD(ds, rid, *args):
    filename = '{}{}.rrd'.format(rrdFolder, rid)

    if len(ds) != len(args):
        raise Exception('number of sources not equivalent to data to write')

    if not os.path.isfile(filename):
        rrdtool.create(filename,
                "--step", "60",
                ds,
                "RRA:AVERAGE:0:1:60",
                "RRA:AVERAGE:0:1:1440",
                "RRA:AVERAGE:0.5:15:672",
                "RRA:AVERAGE:0.5:60:744",
                "RRA:AVERAGE:0.5:60:8760",
                "RRA:MIN:0:1:60",
                "RRA:MIN:0:1:1440",
                "RRA:MIN:0.5:15:672",
                "RRA:MIN:0.5:60:744",
                "RRA:MIN:0.5:60:8760",
                "RRA:MAX:0:1:60",
                "RRA:MAX:0:1:1440",
                "RRA:MAX:0.5:15:672",
                "RRA:MAX:0.5:60:744",
                "RRA:MAX:0.5:60:8760",
                "RRA:LAST:0:1:60",
                "RRA:LAST:0:1:1440",
                "RRA:LAST:0.5:15:672",
                "RRA:LAST:0.5:60:744",
                "RRA:LAST:0.5:60:8760")
    else:
        updateStr =  '{}:{}'.format(dataDate, ':'.join('{}'.format(value) for i,value in enumerate(args)))
        rrdtool.update(filename,
                '--daemon', daemon,
                updateStr)

def updateRRDNode(rid, numClient, numWifi, numVpn):
    updateRRD(dsNodes, rid, numClient, numWifi, numVpn)

def updateRRDTotal(numNode, numClient, numGateway, numNodeOffline, numNodesGeo, numNodesGeoOff):
    updateRRD(dsTotal, 'total', numNode, numClient, numGateway, numNodeOffline, numNodesGeo, numNodesGeoOff)


def write_name_db():
# writes the name database to disk

    try:
        with open(config.get('data', 'namedb'), 'w') as f:
            json.dump(save_name.name_db, f)
    except Exception:
        logger.error('could not write name database to: %s', config.get('data', 'namedb'))


def save_name(clean_id, name):
# saves a nodes name for later lookup

    # empty names are disregarded
    if len(name) == 0:
        return
    
    save_name.name_db[clean_id] = name


# initialize node database as static variable of function save_name()
try:
    with open(config.get('data', 'namedb'), 'r') as f:
        save_name.name_db = json.load(f)
except Exception:
    logger.warning('could not load name database from: %s', config.get('data', 'namedb'))
    save_name.name_db = {}

# database should be written on program termination
atexit.register(write_name_db)

