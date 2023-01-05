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
import time
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
            'endpoint': {},
            'error': None,
            'warning': None,
            'raname':'',
            'version': 0,
            'rapath':''
            }

    def load(self, raname):       
        ''' load the Ra object from a YAML file
        '''
        # obtain the path and the default name of the raname parameters
        ra_file_path = ra_path(raname)
        
        if not os.path.isdir (ra_file_path):
            return False, f'Risk assessment "{raname}" not found'

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

    def save (self):
        ''' saves the Ra object to a YAML file
        '''
        rafile = os.path.join (self.getVal('rapath'),'ra.yaml')
        with open(rafile,'w') as f:
            f.write(yaml.dump(self.dict))

        time_label = time.strftime("_%d%b%Y_%H%M%S", time.localtime()) 
        rahist = os.path.join (self.getVal('rapath'),'hist',f'ra{time_label}.yaml')
        with open(rahist,'w') as f:
            f.write(yaml.dump(self.dict))

    def applyDelta (self, delta_dict):
        ''' uses the keys of the delta_dict parameter to update the contents of self.dict
            - for lists, the content is not appended, but replaced
            - for dictionaries, the content is merged 
        '''
        # update interna dict with keys in the input file (delta)
        black_list = ['raname', 'rapath', 'md5']
        for key in delta_dict:
            if key not in black_list:

                val = delta_dict[key]

                # YAML define null values as 'None, which are interpreted as strings
                if val == 'None':
                    val = None

                if isinstance(val ,dict):
                    for inner_key in val:
                        inner_val = val[inner_key]

                        if inner_val == 'None':
                            inner_val = None

                        self.setInnerVal(key, inner_key, inner_val)
                else:
                    self.setVal(key,val)

    def getVal(self, key):
        ''' returns self.dict value for a given key
        '''
        if key in self.dict:
            return self.dict[key]
        else:
            return None

    def setVal(self, key, value):
        ''' sets self.dict value for a given key, either replacing existing 
            values or creating the key, if it doesn't exist previously
        '''
        # for existing keys, replace the contents of 'value'
        if key in self.dict:
            self.dict[key] = value
        # for new keys, create a new element with 'value' key
        else:
            self.dict[key] = value
           
    def setInnerVal (self, key, inner_key, inner_val):
        ''' sets self.dict for a givenn second level key, either replacing existing 
            values or creating the key, if it doesn't exist previously
        '''
        if not key in self.dict:
            return
        if isinstance(self.dict[key], dict):
            self.dict[key][inner_key] = inner_val
        elif self.dict[key] == None:
            self.dict[key] = {inner_key:inner_val}



    #################################################
    # expert section
    #################################################

    # def extractAction (self, rule):
    #     ''' Returns the ACTION present in the rule
    #     '''
    #     if 'predicate' in rule:
    #         if 'action' in rule['predicate']:
    #             return rule['predicate']['action']
    #     return None

    # def validateRule (self, rule):
    #     ''' Make sure the rule is sythactically correct
    #     '''
    #     # rule should be a dictionary and contain keys 'subject' and 'object' with a list 
    #     if not isinstance(rule, dict):
    #         return False, 'rule is not a dictionary'
    #     if not 'subject' in rule:
    #         return False, 'no subject key in the rule'
    #     if not isinstance(rule['subject'], list):
    #         return False, 'subject key in rule is not of type list'
    #     if not 'object' in rule:
    #         return False, 'no object key in the rule'
    #     if not isinstance(rule['object'], list):
    #         return False, 'object key in the rule is not of type list'
    #     return True, 'OK'


    # def compute (self, rule):
    #     ''' ACTION COMPUTE: we will use information from RA and the rule to generate (compute) additional data
    #         the rule can define if the computation will be run locally or we will call an external service
    #     '''
    #     # rule should be a dictionary and contain keys 'subject' and 'object' with a list 
    #     success, result = self.validateRule(rule)
    #     if not success:
    #         return success, result

    #     print ('COMPUTE actions are not fully implemented yet')

    #     return True, 'OK'

    # def include (self, rule):
    #     ''' ACTION INCLUDE: we will use the rule to include new data in RA, if the elements described in the subject are found
    #         Subject elements can be a list and the conditions will be combined using OR: any element triggers the inclussion
    #     '''
    #     # for any item in the subject
    #     #   if it is coincident with existing keys, add all the elements in the object
    #     success, result = self.validateRule(rule)
    #     if not success:
    #         return success, result

    #     found = False
    #     for isub in rule['subject']:
    #         idic = isub['dic']
    #         ikey = isub['key']
    #         ival = isub['val']
    #         if idic in self.dict:
    #             if isinstance(self.dict[idic],list):
    #                 target_list = self.dict[idic]
    #                 for item in target_list:
    #                     if ikey in item:
    #                         if item[ikey] == ival:
    #                             found = True
    #                             break
    #         if found:
    #             break

    #     if found:
    #         for iobj in rule['object']:

    #             ofound = False
    #             idic = iobj['dic']
    #             ikey = iobj['key']
    #             ival = iobj['val']
            
    #             if idic in self.dict:
    #                 if isinstance(self.dict[idic],list):
    #                     target_list = self.dict[idic]
    #                     for item in target_list:
    #                         if ikey in item:
    #                             if item[ikey] == ival:
    #                                 ofound = True
    #                                 break
    #                     if not ofound:
    #                         new_dict = {ikey: ival}
    #                         self.dict[idic].append(new_dict)

    #                 elif self.dict[idic] is None:
    #                     new_dict = {ikey: ival}
    #                     self.dict[idic] = [new_dict]
        
    #     return True, 'OK'

    # def applyExpert (self):
    #     ''' TODO: we must log all the results of the expert 
    #     '''

    #     expname = os.path.join(self.getVal('rapath'),'expert.json')
    #     if not os.path.isfile(expname):
    #         return False, 'expert.json file not found'

    #     with open(expname, 'r') as f:
    #         ruleset = json.load(f)
        
    #     for rule in ruleset['rule']:

    #         action = self.extractAction(rule)
    #         if action == 'add':
    #             success, result = self.include(rule)
            
    #         elif action == 'request':
    #             print ('REQUEST actions are not implemented yet')

    #         elif action == 'compute':
    #             success, result = self.compute(rule)
            
    #         elif action is None:
    #             return False, 'no valid action found'
        
    #     return success, result

    #################################################
    # output section
    #################################################

    def dumpJSON (self):
        ''' return a JSON version of self.dict
        '''
        return json.dumps(self.dict, allow_nan=True)

    def dumpYAML (self):
        ''' return a human-readable version of self.dir, with a stable order and comments
            for being used as a template in update
        '''
        # open ra.yaml and use the key order and the comments 
        work_dir = os.path.dirname(os.path.abspath(__file__))
        ra_template_name = os.path.join(work_dir,'ra.yaml')
        template=[]
        with open (ra_template_name,'r') as f:
            for line in f:
                template.append(line.strip())

        # list of non-editable items
        blacklist = ['ID', 'error', 'warning', 'raname', 'rapath']

        yaml_out = []
        for iline in template:

            if iline.startswith('#'):
                yaml_out.append(iline)
                continue

            # lines have the format 'substances:         # list of input substances' 
            # use the first part as key, the second as comment
            line = iline.split(':')
            key = line[0]
            if len(line)>1:
                comment = line[-1]

            # do not dump elements which the end-user should not edit
            if key in blacklist : continue

            if key in self.dict:
                value = self.dict[key]

                # value can be a list or a single variable
                if isinstance(value,list):
                    yaml_out.append(f'{key}: {comment}')
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
                    yaml_out.append(f'{key}: {comment}')
                    idict = value
                    for ikey in idict:
                        yaml_out.append (f'  {ikey} : {str(idict[ikey])}')
                
                # item
                else:
                    yaml_out.append(f'{key} : {str(self.dict[key])} {comment}')

        return (yaml_out)

    #################################################
    # utilities section
    #################################################

    def setHash (self):
        ''' Create a md5 hash for a number of keys describing parameters
            relevant for RA
            TODO: not clear which data should be used and what exactly is this useful for
        '''

        # update with any new idata relevant parameter 
        keylist = ['endpoint']

        idata_params = []
        for i in keylist:
            idata_params.append(self.getVal(i))
        
        # use picke as a buffered object, neccesary to generate the hexdigest
        p = pickle.dumps(idata_params)
        self.dict['md5'] = hashlib.md5(p).hexdigest()
