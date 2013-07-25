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
from wsgiref.handlers import format_date_time
from datetime import datetime
from functools import wraps
from time import mktime
import email.utils
import requests
import logging
import pickle

from configuration import config
from retry.decorators import *


logger = logging.getLogger('monitor')


@retry(Exception, tries=4, delay=4)
def get_ff_data():
    """requests new json data from a ff server

    if data was not modified, an exponential back off is used
    to try again 

    """
    file_modified_info = config.get('data', 'lastmodified')

    urls = config.items('dataurl')

    get_ff_data.alt_url += 1
    get_ff_data.alt_url = get_ff_data.alt_url % len(urls)

    modified_info = {}
    headers = {}

    try:
        with open(file_modified_info, 'rb') as fp:
            modified_info = pickle.load(fp)
    
    except IOError:
        logger.warning('could not open last modified info file: %s',
                       file_modified_info)
    
    except Exception:
        logger.error('could not read last modified info from file: %s',
                     file_modified_info)
    
    else:
        if not modified_info['date'] is None:
            headers['If-Modified-Since'] = modified_info['date']
        if not modified_info['etag'] is None:
            headers['If-None-Match'] = modified_info['etag']
    
    r = requests.get(urls[get_ff_data.alt_url][1], headers=headers, timeout=6)
    r.raise_for_status()
    
    if r.status_code == 304:
        get_ff_data.alt_url -= 1
        raise Exception('node list not modified')
    
    elif r.status_code == 200:
        # save modified info for future executions
        if not r.headers['Last-Modified'] is None:
            modified_info['date'] = r.headers['Last-Modified']
    
        else:
            # save current time if no header was present
            now = datetime.now()
            stamp = mktime(now.timetuple())
            modified_info['date'] = format_date_time(stamp)

        if not r.headers['ETag'] is None:
            modified_info['etag'] = r.headers['ETag']
    
        else:
            modified_info['etag'] = None

        try:
            with open(file_modified_info, 'w') as fp:
                pickle.dump(modified_info, fp)
    
        except Exception:
            logger.error('could not write last modified info to file: %s', file_modified_info)

        data_date = str(int(email.utils.mktime_tz(email.utils.parsedate_tz(modified_info['date']))))
        return(r.json, data_date)
    
    else:
        raise Exception('unexpected status code')


get_ff_data.alt_url = -1 # initilize static variable choosing the url to use

