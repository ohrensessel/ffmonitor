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
from operator import itemgetter
import logging
import rrdtool
import time
import os


logger = logging.getLogger('monitor')

# rrd needs some special threatment regarding the series start and end
# otherwise number of returned data points would be wrong
resolution = 60  
series_end = str(int(time.time() / resolution) * resolution)

os.chdir(config.get('rrd', 'path')) # avoid concatenating path and file name for fs operations
daemon = config.get('rrd', 'daemon')


def count_data(rrd_file):
# Count the total number of data points present within now and series_end.
# In addition, the number of unknown data points is returned.
    
    data = rrdtool.fetch(rrd_file,
                        'AVERAGE',
                        '--daemon', daemon,
                        '--resolution', str(resolution),
                        '--end', series_end,
                        '--start', 'end-86400s')
    unknown = 0

    for point in data[2]:
        if point[0] is None:
            unknown += 1

    return(len(data[2]), unknown)


# try to detect missing data due to server faults etc.
_, offset = count_data('total.rrd')

rrd_files = [f for f in os.listdir('.') if os.path.isfile(f)]

offline = {}

# iterate over all rrd files
for rrd_file in rrd_files:
    file_name, file_ext = os.path.splitext(rrd_file)
    
    # total.rrd was threated above
    if not file_ext == '.rrd' or file_name == 'total':
        continue
    
    total, unknown = count_data(rrd_file)
    
    # offset takes data points into account that are unknown because of
    # e.g. server failure
    if total - offset >= 0:
        offline[file_name] = 0
    
    else:
        offline[file_name] = (float(unknown - offset) / (total - offset)) * 100

# sort data so that it can be directly used by php
offline = sorted(offline.iteritems(), key=itemgetter(1), reverse=True)

# write data to file with format 'percentage nodename/mac'
try:
    with open(config.get('stats', 'path'), 'w') as fp:
        for node in offline:
            print(node[1], node[0], file=fp)

except Exception:
    logger.critical('could not write to stats file %s', config.get('stats', 'path'))

