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
            'warning': None,
            'raname':'',
            'version': 0,
            'rapath':''
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
        rafile = os.path.join (self.getVal('rapath'),'ra.yaml')
        with open(rafile,'w') as f:
            f.write(yaml.dump(self.dict))
        print ('save')

    def getJSON (self):
        return json.dumps(self.dict, allow_nan=True)

    def dumpStart (self):
        # add the keys which should be shown to the user uppon the risk assessment creation
        order = ['substances', 'endpoints']
        return self.dump(order)

    def dumpUpdate (self):
        # add the keys which should be shown to the user uppon the risk assessment creation
        order = ['substances', 'endpoints', 'NAMS', 'results']
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
                            for i,ikey in enumerate(idict):
                                if i==0:
                                    yaml_out.append (f'- {ikey:} : {str(idict[ikey])}')
                                else:
                                    yaml_out.append (f'  {ikey:} : {str(idict[ikey])}')

                # dictionary 
                elif isinstance(value,dict):
                    yaml_out.append(f'{key}:')
                    idict = value
                    for ikey in idict:
                        yaml_out.append (f'  {ikey} : {str(idict[ikey])}')
                
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

    #################################################
    # expert section
    #################################################
    def extractAction (self, rule):
        if 'predicate' in rule:
            if 'action' in rule['predicate']:
                return rule['predicate']['action']
        return None

    def validateRule (self, rule):
        # rule should be a dictionary and contain keys 'subject' and 'object' with a list 
        if not isinstance(rule, dict):
            return False, 'rule is not a dictionary'
        if not 'subject' in rule:
            return False, 'no subject key in the rule'
        if not isinstance(rule['subject'], list):
            return False, 'subject key in rule is not of type list'
        if not 'object' in rule:
            return False, 'no object key in the rule'
        if not isinstance(rule['object'], list):
            return False, 'object key in the rule is not of type list'
        return True, 'OK'

    def compute (self, rule):
        # rule should be a dictionary and contain keys 'subject' and 'object' with a list 
        success, result = self.validateRule(rule)
        if not success:
            return success, result

        print ('COMPUTE actions are not fully implemented yet')

        return True, 'OK'

    def addVal(self, rule):
        # for any item in the subject
        #   if it is coincident with existing keys, add all the elements in the object
        success, result = self.validateRule(rule)
        if not success:
            return success, result

        found = False
        for isub in rule['subject']:
            idic = isub['dic']
            ikey = isub['key']
            ival = isub['val']
            if idic in self.dict:
                if isinstance(self.dict[idic],list):
                    target_list = self.dict[idic]
                    for item in target_list:
                        if ikey in item:
                            if item[ikey] == ival:
                                found = True
                                break
            if found:
                break

        if found:
            for iobj in rule['object']:

                ofound = False
                idic = iobj['dic']
                ikey = iobj['key']
                ival = iobj['val']
            
                if idic in self.dict:
                    if isinstance(self.dict[idic],list):
                        target_list = self.dict[idic]
                        for item in target_list:
                            if ikey in item:
                                if item[ikey] == ival:
                                    ofound = True
                                    break
                        if not ofound:
                            new_dict = {ikey: ival}
                            self.dict[idic].append(new_dict)

                    elif self.dict[idic] is None:
                        new_dict = {ikey: ival}
                        self.dict[idic] = [new_dict]
        
        return True, 'OK'


    def appyExpert (self):
        expname = os.path.join(self.getVal('rapath'),'expert.json')
        if not os.path.isfile(expname):
            return False, 'expert.json file not found'

        with open(expname, 'r') as f:
            ruleset = json.load(f)
        
        for rule in ruleset['rule']:

            action = self.extractAction(rule)
            if action == 'add':
                success, result = self.addVal(rule)
            
            elif action == 'request':
                print ('REQUEST actions are not implemented yet')

            elif action == 'compute':
                success, result = self.compute(rule)
            
            elif action is None:
                return False, 'no valid action found'
        
        return True, 'OK'

    #################################################
    # utilities section
    #################################################

    def setHash (self):
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
        self.dict['md5'] = hashlib.md5(p).hexdigest()
