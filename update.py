#!/usr/bin/python
from __future__ import print_function
import logging
import json
from helpers import *

# --------
# see helpers.py for config options
# --------

handler = logging.FileHandler('update.log', 'a') 
format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s') 
handler.setFormatter(format)

logger = logging.getLogger() 
logger.addHandler(handler)


# get (new) json data from ff server
data = json.loads(getFFData())

links = data['links']
nodes = data['nodes']

# init connection counters for each node
for node in nodes:
	node['vpn'] = 0
	node['wifilink'] = 0
	node['client'] = 0

# count connections for each node
for link in links:
    # sanity check
    if not link['type'] in ('vpn', 'client', None):
        # something is wrong, but maybe not critical
        logger.error('unexpected link type: %s', link['type'])
        continue

    if link['type'] is None:
        link['type'] = 'wifilink'
    
    # increase link target and source counters
    nodes[link['source']][link['type']] += 1
    nodes[link['target']][link['type']] += 1 

# init
num_clients = 0
num_gateways = 0
num_gateways_off = 0
num_nodes = 0
num_nodes_off = 0
num_nodes_geo = 0
num_nodes_geo_off = 0


def get_clean_id(id):
    # removes colons from node id
    return id.replace(':', '')


for node in nodes:
    flags = node['flags']
    
    # clients are always online, so we do not need to check that
    if flags['client']:
        num_clients += 1

    else:
        # gateways and nodes are treated equally
        if flags['online']:
            clean_id = get_clean_id(node['id'])
            
            #update_rrd_node(clean_id, node['client'], node['wifilink'], node['vpn'])
            print(clean_id,  node['client'], node['wifilink'], node['vpn'])
            #save_name(clean_id, node['name'])

            # is a gateway
            if flags['gateway']:
                num_gateways += 1
                
            # is a node
            else:
                num_nodes += 1

                if not node['geo'] is None:
                    num_nodes_geo += 1          

        else:
            # delete rrd files for nodes offline > 1 month?
            # create rrd file for nodes never seen before?
            #check_offline_node()

            if flags['gateway']:
                num_gateways_off += 1            

            else:
                num_nodes_off += 1
            
                if not node['geo'] is None:
                    num_nodes_geo_off += 1


# nodes are no clients
num_clients -= num_nodes

print(num_nodes, num_clients, num_gateways, num_nodes_off, num_nodes_geo, num_nodes_geo_off)
#update_rrd_total(num_nodes, num_clients, num_gateways, num_nodes_off, num_nodes_geo, num_nodes_geo_off)

