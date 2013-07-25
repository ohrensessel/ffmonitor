#!/usr/bin/python
from configuration import config
import os.path
import rrdtool
import logging


logger = logging.getLogger('monitor')


def _get_ds_def(src_def):
# creates a data source definition for rrd tool
    
    src_str = 'DS:{}:GAUGE:120:0:32768'   

    return [src_str.format(a_src) for a_src in src_def]


src_nodes = ['clients', 'wifilinks', 'vpns']
ds_nodes = _get_ds_def(src_nodes)

src_total = ['nodes', 'clients', 'gateways', 'nodesoffline', 'nodesgeo',
             'nodesoffgeo']
ds_total = _get_ds_def(src_total)


def _create_rrd(filename, data_src):
# creates a new rrd file when it does not yet exist
    
    if not os.path.isfile(filename):
        rra_types = ['AVERAGE', 'MIN', 'MAX', 'LAST']    
    
        rra_strs = ['RRA:{}:0:1:60', 
                    'RRA:{}:0:1:1440',
                    'RRA:{}:0.5:15:672',
                    'RRA:{}:0.5:60:744',
                    'RRA:{}:0.5:60:8760']

        rra = [rra_str.format(rra_type) for rra_type in rra_types
               for rra_str in rra_strs]
        
        rrdtool.create(filename,
                       '--step', '60',
                        data_src,
                        rra)


daemon = config.get('rrd', 'daemon')
rrd_path = config.get('rrd', 'path')


# save data to rrd files
def _update(data_src, clean_id, *args):
    filename = ''.join([rrd_path, clean_id, '.rrd'])
    
    # ensure rrd file existence
    _create_rrd(filename, data_src)

    # concatenate date and values
    update_str = ':'.join([str(value) for value in args])
     
    rrdtool.update(filename,
                   '--daemon', daemon,
                   update_str)


def update_node(clean_id, date, num_clients, num_wifis, num_vpns):
    """update a nodes rrd file with new data

    Keyword arguments:
    clean_id -- the id of the node without colons
    date -- the date and time the data was acquired
    num_* -- the numbers to write to the rrd file

    """
    _update(ds_nodes, clean_id, date, num_clients, num_wifis, num_vpns)


def update_total(date, num_nodes, num_clients, num_gateways, num_nodes_off,
                 num_nodes_geo, num_nodes_geo_off):
    """update the mesh size rrd file with new data

    Keyword arguments:
    date -- the date and time the data was acquired
    num_* -- the numbers to write to the rrd file

    """
    _update(ds_total, 'total', date, num_nodes, num_clients, num_gateways,
              num_nodes_off, num_nodes_geo, num_nodes_geo_off)

