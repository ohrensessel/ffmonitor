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
import json
import re

class NameDB:
    
    database = None
    macs = None

    logger = None
    

    def __init__(self):
        self.logger = logging.getLogger('monitor')
        

        def read_data(db):
            try:
                with open(config.get('data', db), 'r') as fp:
                    return json.load(fp)

            except Exception:
                return {}


        self.database = read_data('namedb')
        self.macs = read_data('macdb')
        

    def __del__(self):
        

        def save_data(db, var):
            try:
                with open(config.get('data', db), 'w') as fp:
                    json.dump(var, fp)

            except Exception:
                self.logger.error('could not write %s to: %s',
                                  db, config.get('data', db))


        save_data('namedb', self.database)
        save_data('macdb', self.macs)


    def get_name(self, id):
        """returns the name associated with the given id

        Arguments:
        id -- a node id (without colons)

        """
        if id in self.database:
            return self.database[id]
        
        else:
            return ':'.join(id[i:i+2] for i in xrange(0, len(id), 2))
    
    
    def name_exists(self, name):
        """checks whether a name exists in the database

        Arguments:
        name -- name to look up

        """        
        for entry in self.database:
            if self.database[entry] == name:
                return True

        return False


    def get_id(self, expected_id):
        """returns the id to a given mac adress

        Arguments:
        expected_id -- mac which is expected to be the id

        """
        # given id is the real id
        if expected_id in self.macs:
            return expected_id
        
        # search for mac in database
        for node_id in self.macs:
            # mac found -> return associated id
            for mac in self.macs[node_id]:
                if expected_id in mac:
                    return node_id

        # nothing found
        return expected_id
 

    def is_id(self, expected_id):
        """checks wether a given mac is an id
        
        Arguments:
        expected_id -- mac which is expected to be the id

        """
        if expected_id == self.get_id(expected_id):
            return True
        else:
            return False
  
    
    def get_id_from_name(self, search_name):
        """returns the id to a given name

        Arguments:
        search_name -- name to look up

        """
        for node_id, name in enumerate(self.database):
            if name == search_name:
                return node_id

        return None

    def get_match(self, reg):
        """returns the id of node names matching the given regular expression

        Arguments:
        reg -- regular expression to match

        """
        red = redict(zip(self.database.values(), self.database.keys()))
        return red[reg]


class WriteableNameDB(NameDB):

    def save_name(self, name, node_id, *macs):
        """saves a node in the database

        if the node is present, its entries are updated

        Arguments:
        name -- node name
        node_id -- node id
        macs -- additional macs of the node

        """
        node_id = self.get_id(node_id)

        self.database[node_id] = name        
        
        macs = list(macs)
        macs = [str(x.replace(':', '')) for x in macs]
        
        if node_id in self.macs:
            self.macs[node_id] = list(set(self.macs[node_id] + macs))
        else:
            self.macs[node_id] = macs


class redict(dict):
    def __init__(self, d):
        dict.__init__(self, d)

    def __getitem__(self, regex):
        r = re.compile(regex)
        mkeys = filter(r.match, self.keys())
        for i in mkeys:
                yield dict.__getitem__(self, i)
