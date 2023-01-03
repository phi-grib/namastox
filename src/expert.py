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

import json
import yaml
import os
from utils import ra_path

class Expert:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self, raname, version):
        ''' constructor '''
        self.rules = []
        self.rapath = ra_path(raname, version)

    def load(self):       
        ''' load the Expert object from a JSON file
        '''
        expname = os.path.join(self.rapath,'expert.yaml')
        if not os.path.isfile(expname):
            return False, 'expert.yaml file not found'

        with open(expname, 'r') as f:
            expert_import = yaml.safe_load(f)
            if 'rules' in expert_import:
                self.rules = expert_import['rules']
            else:
                return False, f'incorrect synthax in file {expname}'
        
        return True, 'OK'

    def save (self):
        ''' saves the Expert object to a JSON file
        '''
        expname = os.path.join (self.rapath,'expert.yaml')
        with open(expname,'w') as f:
            f.write(yaml.dump({"rules":self.rules}))

    def extractAction (self, rule):
        ''' Returns the ACTION present in the rule
        '''
        if not isinstance(rule, list):
            return None
        if len(rule)<3:
            return None
        if 'action' in rule[1]:
                return rule[1]['action']
        return None

    def validateRule (self, rule):
        ''' Make sure the rule is sythactically correct
        '''
        # rule should be a list of three items 
        if not isinstance(rule, list):
            return False, 'rule is not a list'
        if len(rule)<3:
            return False, 'rule length should be 3'
        if not isinstance(rule[0], dict):
            return False, 'first item in rule is not of type dictionary'
        if not isinstance(rule[1], dict):
            return False, 'second item in rule is not of type dictionary'
        if not isinstance(rule[2], dict):
            return False, 'third item in rule is not of type dictionary'
        return True, 'OK'

    def compute (self, rule, ra):
        ''' ACTION COMPUTE: we will use information from RA and the rule to generate (compute) additional data
            the rule can define if the computation will be run locally or we will call an external service
        '''
        # rule should be a dictionary and contain keys 'subject' and 'object' with a list 
        success, result = self.validateRule(rule)
        if not success:
            return success, result

        print ('COMPUTE actions are not fully implemented yet')

        return True, 'OK'

    def include (self, rule, ra):
        ''' ACTION INCLUDE: we will use the rule to include new data in RA, if the elements described in the subject are found
            Subject elements can be a list and the conditions will be combined using OR: any element triggers the inclussion
        '''
        # for any item in the subject
        #   if it is coincident with existing keys, add all the elements in the object
        success, result = self.validateRule(rule)
        if not success:
            return success, result

        rdic = ra.dict

        found = False
        sdic = rule[0]   
        sub_name = sdic['dict'] # for example sub_name = 'endpoints'
        sdic.pop('dict')
        if sub_name in rdic:
            rdic_sub = rdic[sub_name]
            if isinstance(rdic_sub,list):
                for irdic in rdic_sub: 
                    for skey in sdic:
                        if skey in irdic:
                            if irdic[skey]==sdic[skey]:
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break

        if found:
            odic = rule[2]
            obj_name = odic['dict']
            odic.pop('dict')
            odic['status']='pending'
            if obj_name in rdic:
                rdic_obj = rdic[obj_name]
                if isinstance(rdic_obj,list):
                    ra.dict[obj_name].append(odic)
                else:
                    ra.dict[obj_name]=[odic]
        
        return True, 'OK'

    def applyExpert (self, ra):
        ''' TODO: we must log all the results of the expert 
        '''
        
        for rule in self.rules:

            action = self.extractAction(rule)
            if action == 'add':
                success, result = self.include(rule, ra)
            
            elif action == 'request':
                print ('REQUEST actions are not implemented yet')

            elif action == 'compute':
                success, result = self.compute(rule, ra)
            
            elif action is None:
                return False, 'no valid action found'
        
        return success, result