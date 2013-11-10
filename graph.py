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
from __future__ import print_function
from configuration import config
import logging
import rrdtool
from NameDB import NameDB
import os


logger = logging.getLogger('monitor')
namedb = NameDB()

daemon = config.get('rrd', 'daemon')
graph_path = config.get('graph', 'path')

# define witch graphs to generate
gen_graphs = {'hour': '60min', 'day': '24h', 'week': '168h', 'month': '744h',
              'year': '8760h' }

# rrdtool specific stuff
# for node graphs
node_defs = ['DEF:gclient={}:clients:AVERAGE',
             'DEF:gwifi={}:wifilinks:AVERAGE',
             'DEF:gvpn={}:vpns:AVERAGE']
node_lines = []
node_lines.append('COMMENT:          ')
node_lines.append('COMMENT:         Cur')
node_lines.append('COMMENT:       Max')
node_lines.append('COMMENT:       Min')
node_lines.append('COMMENT:       Avg')
node_lines.append('LINE:gclient#00008B:Clients   ')
node_lines.append('GPRINT:gclient:LAST:%8.2lf')
node_lines.append('GPRINT:gclient:MAX:%8.2lf')
node_lines.append('GPRINT:gclient:MIN:%8.2lf')
node_lines.append('GPRINT:gclient:AVERAGE:%8.2lf')
node_lines.append('LINE:gwifi#006400:WLAN      ')
node_lines.append('GPRINT:gwifi:LAST:%8.2lf')
node_lines.append('GPRINT:gwifi:MAX:%8.2lf')
node_lines.append('GPRINT:gwifi:MIN:%8.2lf')
node_lines.append('GPRINT:gwifi:AVERAGE:%8.2lf')
node_lines.append('LINE:gvpn#FF8C00:VPN       ')
node_lines.append('GPRINT:gvpn:LAST:%8.2lf')
node_lines.append('GPRINT:gvpn:MAX:%8.2lf')
node_lines.append('GPRINT:gvpn:MIN:%8.2lf')
node_lines.append('GPRINT:gvpn:AVERAGE:%8.2lf')

# for mesh size graph
total_defs = ['DEF:gclient={}:clients:AVERAGE',
              'DEF:gnodes={}:nodes:AVERAGE',
              'DEF:ggw={}:gateways:AVERAGE',
              'DEF:gnodesoff={}:nodesoffline:AVERAGE']
total_lines = []
total_lines.append('COMMENT:          ')
total_lines.append('COMMENT:         Cur')
total_lines.append('COMMENT:       Max')
total_lines.append('COMMENT:       Min')
total_lines.append('COMMENT:       Avg')
total_lines.append('AREA:gnodes#00CC00:Nodes     ')
total_lines.append('GPRINT:gnodes:LAST:%8.2lf')
total_lines.append('GPRINT:gnodes:MAX:%8.2lf')
total_lines.append('GPRINT:gnodes:MIN:%8.2lf')
total_lines.append('GPRINT:gnodes:AVERAGE:%8.2lf')
total_lines.append('AREA:gnodesoff#FFCC00:Nodes Off.:STACK')
total_lines.append('GPRINT:gnodesoff:LAST:%8.2lf')
total_lines.append('GPRINT:gnodesoff:MAX:%8.2lf')
total_lines.append('GPRINT:gnodesoff:MIN:%8.2lf')
total_lines.append('GPRINT:gnodesoff:AVERAGE:%8.2lf')
total_lines.append('LINE:ggw#FF8C00:Gateways  ')
total_lines.append('GPRINT:ggw:LAST:%8.2lf')
total_lines.append('GPRINT:ggw:MAX:%8.2lf')
total_lines.append('GPRINT:ggw:MIN:%8.2lf')
total_lines.append('GPRINT:ggw:AVERAGE:%8.2lf')
total_lines.append('LINE:gclient#0066B3:Clients   ')
total_lines.append('GPRINT:gclient:LAST:%8.2lf')
total_lines.append('GPRINT:gclient:MAX:%8.2lf')
total_lines.append('GPRINT:gclient:MIN:%8.2lf')
total_lines.append('GPRINT:gclient:AVERAGE:%8.2lf')

# avoid concatenating path and file name for fs operations
os.chdir(config.get('rrd', 'path'))

rrd_files = [f for f in os.listdir('.') if os.path.isfile(f)]


def get_def(rrd_file, defs):
# generates the rrdtool DEF lines

    return [a_def.format(rrd_file) for a_def in defs]


for rrd_file in rrd_files:
    file_name, file_ext = os.path.splitext(rrd_file)

    # there may be other files in the directory    
    if not file_ext == '.rrd':
        continue   
 
    # handle nodes and mesh size (total) graph separately
    if not file_name == 'total': # node graph
        # only graph node ids, not macs
        if not namedb.is_id(file_name):
            continue

        defs = get_def(rrd_file, node_defs)
        lines = node_lines
        
        title = 'node {}'.format(namedb.get_name(file_name).encode('ascii', 'ignore'))
        vlabel = '# connections'

    else: # total graph
        defs = get_def(rrd_file, total_defs) 
        lines = total_lines

        title = 'mesh size'
        vlabel = '# hosts'  
    
    img_base_name = ''.join([graph_path, file_name])    

    # generate pngs
    for range_name, range_duration  in gen_graphs.iteritems():
        complete_title = ''.join([title, ' - by ', range_name])
        
        img_name = ''.join([img_base_name, '_', range_name, '.png'])
        
        rrdtool.graph(img_name,
                '--title', complete_title,
                '--lazy',
                '--imgformat', 'PNG',
                '--width', '400',
                '--height', '175',
                '--end', 'now', '--start', 'end-' + range_duration, 
                '--vertical-label', vlabel,
                '--lower-limit', '0',
                '--daemon', daemon,
                defs,
                lines)

