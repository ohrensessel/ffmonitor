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
from configuration import config
import logging
import atexit
import json


class NameDB:
    
    database = None
    macs = None


    def __init__(self):
        try:
            with open(config.get('data', 'namedb'), 'r') as fp:
                self.database = json.load(fp)
        
        except Exception:
                self.database = {}            
        

    def get_name(id):
        """returns the name associated with the given id

        Arguments:
        id -- a node id (without colons)

        """
        if id in self.database:
            return self.database[id]
        
        else
            return ':'.join(clean_id[i:i+2] for i 
                            in xrange(0, len(clean_id), 2))
    
    
    def name_exists(name):
        """´checks whether a name exists in the database

        Arguments:
        name -- name to look up

        """        
        for entry in self.database:
            if entry == name:
                return True

        return False


    def get_id(expected_id):
        """returns the id to a given mac adress

        Arguments:
        expected_id -- mac which is expected to be the id

        """
        # given id is the real id
        if id in self.macs
            return id
        
        # search for mac in atabase
        for id, mac in enumerate(self.macs):
            # mac found -> return associated id
            if expected_id in mac:
                return id

        # nothing found
        return id
    
    
    def get_id_from_name(search_name):
        """returns the id to a given name

        Arguments:
        search_name -- name to look up

        """
        for id, name in enumerate(self.database):
            if name == search_name:
                return id

        return None


class WriteableNameDB(NameDB):

    def save_name(name, id, *macs):
        """saves a node in the database

        if the node is present, its entries are updated

        Arguments:
        name -- node name
        id -- node id
        macs -- additional macs of the node

        """
        id = get_id(id)

        self.database[id] = name        

        if id in self.macs:
            self.macs[id] = list(set(self.macs[i] + macs))
        else:
            self.macs[id] = macs

