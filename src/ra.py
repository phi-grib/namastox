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
import shutil
import yaml
import os
import time
import hashlib
from src.utils import ra_path
from src.workflow import Workflow
from src.logger import get_logger
LOG = get_logger(__name__)

class Ra:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self, raname):
        ''' constructor '''

        # internal data
        self.raname = raname
        self.rapath = ra_path(raname)
        self.workflow = None  
        
        # default, these are loaded from a YAML file
        self.ra = {
            'ID': None,
            'workflow_name': None,
            'step': 0,
            'active_nodes_id': []
        }
        self.general = {
            'endpoint': {},
            'administration_route': None,
            'species': None,
            'regulatory_frameworks': None,
            'substances': []
        }
        self.results = []
        self.notes = []
        self.assessment = None
        
    def load(self):       
        ''' load the Ra object from a YAML file
        '''
        # obtain the path and the default name of the raname parameters
        if not os.path.isdir (self.rapath):
            return False, f'Risk assessment "{self.rapath}" not found'

        # load the main class dictionary (p) from this yaml file
        ra_file_name = os.path.join (self.rapath,'ra.yaml')
        if not os.path.isfile(ra_file_name):
            return False, f'Risk assessment definition {ra_file_name} file not found'

        yaml_dict = {}
        try:
            with open(ra_file_name, 'r') as pfile:
                yaml_dict = yaml.safe_load(pfile)
        except Exception as e:
            return False, e

        #TODO: validate yaml_dict
        keylist = ['ra', 'general', 'results', 'notes', 'assessment']
        for ikey in keylist:
            if yaml_dict[ikey]!=None:
                # print (f'loading {ikey} : {yaml_dict[ikey]}')
                self.__dict__[ikey]=yaml_dict[ikey]

        self.workflow = Workflow(self.raname, self.ra['workflow_name'])
        self.workflow.import_table()

        return True, 'OK'

    def save (self):
        ''' saves the Ra object to a YAML file
        '''
        rafile = os.path.join (self.rapath,'ra.yaml')
        dict_temp = {
            'ra': self.ra,
            'general': self.general, 
            'results': self.results,
            'notes': self.notes,
            'assessment': self.assessment
        }
        with open(rafile,'w') as f:
            f.write(yaml.dump(dict_temp))

        time_label = time.strftime("_%d%b%Y_%H%M%S", time.localtime()) 
        rahist = os.path.join (self.rapath,'hist',f'ra{time_label}.yaml')
        shutil.copyfile(rafile, rahist)


    # def applyDelta (self, delta_dict):
    #     ''' uses the keys of the delta_dict parameter to update the contents of self.dict
    #         - for lists, the content is not appended, but replaced
    #         - for dictionaries, the content is merged 
    #     '''
    #     # update interna dict with keys in the input file (delta)
    #     black_list = ['raname', 'rapath', 'md5']
    #     for key in delta_dict:
    #         if key not in black_list:

    #             val = delta_dict[key]

    #             # yaml define null values as 'None', which are interpreted as strings
    #             if val == 'None':
    #                 val = None

    #             if isinstance(val ,dict):
    #                 for inner_key in val:
    #                     inner_val = val[inner_key]

    #                     if inner_val == 'None':
    #                         inner_val = None

    #                     self.setInnerVal(key, inner_key, inner_val)
    #             else:
    #                 self.setVal(key,val)

    def update(self, input):
        ''' validate result and if it matchs the requirements of an active node progress in the workflow'''

        # validate result
        step = self.ra['step']

        # special case of the first step
        if step == 0:
            if not 'general' in input:
                return False, 'wrong format in input file (no "general" info)'
            self.general = input['general']

            # set firstnode as active node
            active_node = self.workflow.firstNode()
            self.ra['active_nodes_id']=[active_node.getVal('id')]
            LOG.info(f'active node updated to: {self.ra["active_nodes_id"]}' )

            # advance workflow: step+1
            LOG.info(f'workflow advanced to step: {step+1}')
            self.ra['step']=step+1

            self.save()

            return True, 'OK'
        
        if not 'result' in input:
            return False, 'wrong format in input file (no "result" info)'
        
        input_result = input['result']
        
        # identify the node for which this result has been obtained
        input_node_id = input_result['id']

        # validate input, the template must be tagged for this workflow node
        if not input_node_id in self.ra["active_nodes_id"]:
            LOG.error(f'input for node {input_node_id} not in the active nodes list({self.ra["active_nodes_id"]})')
            return False, 'incorrect input'

        # append result
        input_node = self.workflow.getNode(input_node_id)
        self.results.append(input_result)

        # if logical find new active node (method in workflow?)
        if input_node.getVal('cathegory') == 'LOGICAL':
            self.ra['active_nodes_id'] = self.workflow.logicalNodeList(input_node_id, input_result['decision'])
            LOG.info(f'active node updated to: {self.ra["active_nodes_id"]}, based on decision {input_result["decision"]}' )
        else:
            self.ra['active_nodes_id'] = self.workflow.nextNodeList(input_node_id)
            LOG.info(f'active node updated to: {self.ra["active_nodes_id"]}' )


        # advance workflow: step+1, active workflow+1
        self.ra['step']=step+1
        LOG.info(f'workflow advanced to step: {step+1}')

        self.save()

        return True, 'OK'

    def getVal(self, key):
        ''' returns self.dict value for a given key
        '''
        if key in self.ra:
            return self.ra[key]
        else:
            return None

    def setVal(self, key, value):
        ''' sets self.dict value for a given key, either replacing existing 
            values or creating the key, if it doesn't exist previously
        '''
        # for existing keys, replace the contents of 'value'
        if key in self.ra:
            self.ra[key] = value
        # for new keys, create a new element with 'value' key
        else:
            self.ra[key] = value
           
 
    #################################################
    # output section
    #################################################

    def dumpYAML (self):
        ''' dumps a template of the results for the following active nodes
        '''
        current_step = self.ra['step']
        results = f'# template for step {current_step}\n'
        if current_step == 0:
            results+= yaml.dump({'general':self.general})
        else:
            results = ''
            for iid in self.ra['active_nodes_id']:
                inode = self.workflow.getNode(iid)
                results+= f'# node {inode.getVal("name")}\n'

                itask = inode.getTask()
                results+= itask.getTemplate()

        return results


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
