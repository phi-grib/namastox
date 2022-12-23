#! -*- coding: utf-8 -*-

# Description    NAMASTOX command
#
# Authors:       Manuel Pastor (manuel.pastor@upf.edu)
#
# Copyright 2022 Manuel Pastor
#
# This file is part of NAMASTOX
#
# NAMASTOX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.
#
# Flame is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NAMASTOX. If not, see <http://www.gnu.org/licenses/>.

import pickle
import numpy as np
import json
import yaml
import os
import hashlib
from utils import ra_path

class NAM:
    def __init__(self, name, description=None):
        self.name = name
        self.decription = description

class substance:
    def __init__(self, name, ID, CASRN=None, SMILES=None):
        self.name = name
        self.ID = ID
        self.CASRN=CASRN
        self.SMILES=SMILES

class endpoint:
    def __init__(self, name, description=None):
        self.name = name
        self.decription = description

class Ra:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self):
        ''' constructor '''
        self.dict = {
            'ID':{}, 
            'results':{},
            'NAMS':[],
            'substances':[],
            'endpoints':[],
            'error': None,
            'warning': None
            }

    def loadYaml(self, raname, version):       
        ''' load the ra object from a YAML file
        '''
        # obtain the path and the default name of the raname parameters
        ra_file_path = ra_path(raname, version)
        
        if not os.path.isdir (ra_file_path):
            return False, f'Risk assessment "{raname}", version "{version}" not found'

        ra_file_name = os.path.join (ra_file_path,'ra.yaml')

        # load the main class dictionary (p) from this yaml file
        if not os.path.isfile(ra_file_name):
            return False, f'Risk assessment definition {ra_file_name} file not found'

        try:
            with open(ra_file_name, 'r') as pfile:
                self.dict = yaml.safe_load(pfile)
        except Exception as e:
            return False, e

        # add keys for the raname and a MD5 hash
        self.setVal('raname',raname)
        self.setVal('version',version)
        self.setVal('rapath',ra_file_path)
        self.setVal('md5',self.idataHash())

        return True, 'OK'

    def applyDelta (self, delta_dict):
        # update interna dict with keys in the input file (delta)
        black_list = ['raname', 'version', 'rapath', 'md5']
        for key in delta_dict:
            if key not in black_list:

                val = delta_dict[key]

                # YAML define null values as 'None, which are interpreted 
                # as strings
                if val == 'None':
                    val = None

                if isinstance(val ,dict):
                    for inner_key in val:
                        inner_val = val[inner_key]

                        if inner_val == 'None':
                            inner_val = None

                        self.setInnerVal(key, inner_key, inner_val)
                        #print ('@delta: adding',key, inner_key, inner_val)
                else:
                    self.setVal(key,val)

    def load (self):
        print ('load')

    def save (self):
        print ('save')

    def getJSON (self):
        return json.dumps(self.dict, allow_nan=True)

    def dumpStart (self):
        # add the keys which should be shown to the user uppon the risk assessment creation
        order = ['substances', 'endpoints']
        return self.dump(order)

    def dumpUpdate (self):
        # add the keys which should be shown to the user uppon the risk assessment creation
        order = ['substances', 'endpoints', 'results']
        return self.dump(order)

    def dump (self, elements):
        yaml_out = []
        for key in elements:
            if key in self.dict:
                value = self.dict[key]

                # value can be a list or a single variable
                if isinstance(value,list):
                    yaml_out.append(f'{key}:')
                    for iitem in value:

                        # list item is a value
                        if not isinstance(iitem, dict):
                            yaml_out.append (f'- {iitem}')
                        
                        # list item is a dictionary
                        else:
                            idict = iitem
                            for ikey in idict:
                                yaml_out.append (f'- {ikey:} : ')
                                iidict = idict[ikey]
                                for iikey in iidict:
                                    yaml_out.append (f'   {iikey} : {str(iidict[iikey])}')

                # dictionary 
                elif isinstance(value,dict):
                    yaml_out.append(f'{key}:')
                    idict = value
                    for ikey in idict:
                        yaml_out.append (f'   {ikey} : {str(idict[ikey])}')
                
                # item
                else:
                    yaml_out.append(f'{key} : {str(self.dict[key])}')

        return (yaml_out)

    def setVal(self, key, value):
        # for existing keys, replace the contents of 'value'
        if key in self.dict:
            self.dict[key] = value
        # for new keys, create a new element with 'value' key
        else:
            self.dict[key] = value
        
    def setInnerVal (self, ext_key, key, value):
        # for existing keys, replace the contents of 'value'
        if not key in self:
            return
        inner = self.dict[key]
        if key in inner:
            inner[key] = value
        # for new keys, create a new element with 'value' key
        else:
            inner[key] = value

    def getVal(self, key):
        if key in self.dict:
            return self.dict[key]
        else:
            return None

    def idataHash (self):
        ''' Create a md5 hash for a number of keys describing parameters
            relevant for idata

            This hash is compared between runs, to check wether idata must
            recompute or not the MD 
        '''

        # update with any new idata relevant parameter 
        keylist = ['endpoint','version']

        idata_params = []
        for i in keylist:
            idata_params.append(self.getVal(i))
        
        # use picke as a buffered object, neccesary to generate the hexdigest
        p = pickle.dumps(idata_params)
        return hashlib.md5(p).hexdigest()