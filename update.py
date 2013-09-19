#!/usr/bin/env python
#
# ffmonitor - a monitoring tool for freifunk networks
# Copyright (C) 2013  Leo Krueger
# 
# This file is part of ffmonitor.
#
# ffmonitor is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ffmonitor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ffmonitor.  If not, see <http://www.gnu.org/licenses/>.
#
from NameDB import WriteableNameDB
import data
import rrd
import log


logger = log.init_custom_logger('monitor')
namedb = WriteableNameDB()


# get (new) json data from ff server
data, date = data.get_ff_data()

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
    
    return str(id.replace(':', ''))


for node in nodes:
    flags = node['flags']
    
    # clients are always online, so we do not need to check that
    if flags['client']:
        num_clients += 1

    else:
        # gateways and nodes are treated equally
        if flags['online']:
            clean_id = get_clean_id(node['id'])
            clean_id = namedb.get_id(clean_id)

            namedb.save_name(node['name'], clean_id, node['macs'])

            # is a gateway
            if flags['gateway']:
                num_gateways += 1
                
            # is a node
            else:
                num_nodes += 1

                # decrease number of clients by one,
                # as the node itself is also counted as its client
                if node['client'] > 0:
                    node['client'] -= 1

                if not node['geo'] is None:
                    num_nodes_geo += 1          

            rrd.update_node(clean_id, date, node['client'], node['wifilink'], node['vpn'])

        else:
            # delete rrd files for nodes offline > 1 month?
            # create rrd file for nodes never seen before?
            # rrd.check_offline_node(clean_id)

            if flags['gateway']:
                num_gateways_off += 1            

            else:
                num_nodes_off += 1
            
                if not node['geo'] is None:
                    num_nodes_geo_off += 1


# nodes are no clients
num_clients -= num_nodes

rrd.update_total(date, num_nodes, num_clients, num_gateways, num_nodes_off, num_nodes_geo, num_nodes_geo_off)

