#!/usr/bin/python
from __future__ import print_function
from operator import itemgetter
import ConfigParser
import rrdtool
import time
import os


config = ConfigParser.RawConfigParser()
config.read('monitoring.conf')

daemon = config.get('rrd', 'daemon')
rrd_path = config.get('rrd', 'path')
stat_file = config.get('stats', 'path')

# rrd needs some special threatment regarding the series start and end
# otherwise number of returned data points would be wrong
resolution = 60  
series_end = str(int(time.time() / resolution) * resolution)

os.chdir(rrd_path) # avoid concatenating path and file name for fs operations

# try to detect missing data due to server faults etc.
_, offset = count_data('total.rrd')

rrd_files = [f for f in os.listdir('.') if os.path.isfile(f)]

offline = {}


def count_data(rrd_file):
# Count the total number of data points present within now and series_end.
# In addition, the number of unknown data points is returned.

    data = rrdtool.fetch(rrd_file,
                        'AVERAGE',
                        '--daemon', daemon,
                        '--resolution', '60',
                        '--end', series_end,
                        '--start', 'end-86400s')
    unknown = 0

    for point in data[2]:
        if point[0] is None:
            unknown += 1

    return(len(data[2]), unknown)


# iterate over all rrd files
for rrd_file in rrd_files:
    file_name, file_ext = os.path.splitext(rrd_file)
    
    # total.rrd was threated above
    if not file_ext == '.rrd' or file_name == 'total':
        continue
    
    total, unknown = count_data(rrd_file)
    
    # offset takes data points into account that are unknown because of
    # e.g. server failure
    offline[file_name] = (float(unknown - offset) / (total - offset)) * 100

# sort data so that it can be directly used by php
offline = sorted(offline.iteritems(), key=itemgetter(1), reverse=True)

# write data to file with format 'percentage nodename/mac'
with open(stat_file, 'w') as fp:
    for node in offline:
        print(node[1], node[0], file=fp)

