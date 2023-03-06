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
from namastox.utils import ra_path
from namastox.workflow import Workflow
from namastox.logger import get_logger
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
        self.workflow_path
        
        # default, these are loaded from a YAML file
        self.ra = {
            'ID': None,
            'workflow_name': None,
            'step': 0,
            'active_nodes_id': []
        }
        self.general = {
            'endpoint': {},
            'title': None,
            'problem_formulation': None,
            'uncertainty': None, 
            'administration_route': None,
            'species': None,
            'regulatory_frameworks': None,
            'workflow_custom': None,
            'substances': []
        }
        self.results = []
        self.notes = []
        self.assessment = None


    def load(self, step=None):       
        ''' load the Ra object from a YAML file
        '''
        # obtain the path and the default name of the raname parameters
        if not os.path.isdir (self.rapath):
            return False, f'Risk assessment "{self.rapath}" not found'

        # load the main class dictionary (p) from this yaml file
        ra_file_name = os.path.join (self.rapath,'ra.yaml')
        if not os.path.isfile(ra_file_name):
            return False, f'Risk assessment definition {ra_file_name} file not found'

        # load status from yaml
        yaml_dict = {}
        try:
            with open(ra_file_name, 'r') as pfile:
                yaml_dict = yaml.safe_load(pfile)
        except Exception as e:
            return False, e
        
        # if a defined step is requested
        if step is not None:
            try:
                step = int(step)
            except:
                return False, 'step must be a positive int'

            found = False
            # check first if the requested step is the last one
            if not self.checkStep(yaml_dict, step):
                ra_hist_path = os.path.join (self.rapath,'hist')
                for ra_hist_file in os.listdir(ra_hist_path):
                    ra_hist_item = os.path.join(ra_hist_path, ra_hist_file)
                    if os.path.isfile(ra_hist_item):
                        idict = {}
                        with open(ra_hist_item, 'r') as pfile:
                            idict = yaml.safe_load(pfile)
                        if self.checkStep(idict, step):
                            yaml_dict = idict
                            found = True
                            break
                                
                if not found:
                    return False, 'step not found'                

        # validate yaml_dict
        keylist = ['ra', 'general', 'results', 'notes', 'assessment']
        for ikey in keylist:
            if yaml_dict[ikey]!=None:
                self.__dict__[ikey]=yaml_dict[ikey]

        # load workflow
        if self.ra['step']>0 : 
            self.workflow = Workflow(self.raname, self.ra['workflow_name'])

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

    def getStatus(self):
        ''' return a dictionary with RA status'''
        return {'ra':self.ra}

    def getActiveNodes (self):
        ''' returns a list with the active nodes'''
        active_nodes_id = self.ra['active_nodes_id']
        olist = []
        
        if active_nodes_id is None:
            return olist

        for node_id in active_nodes_id:
            input_node = self.workflow.getNode(node_id)
            itask = input_node.getTask()
            olist.append({'id':node_id, 
                           'description':itask.getDescriptionText(),
                           'cathegory':itask.getCathegoryText()})
        return olist
    
    def getActiveNode (self, node_id):
        active_nodes_id = self.ra['active_nodes_id']
        if node_id in active_nodes_id:
            input_node = self.workflow.getNode(node_id)
            itask = input_node.getTask()
            return (itask.getTemplateDict())
        return None

    def getResults(self):
        ''' return a list with RA results'''
        return self.results

    def getNotes(self):
        ''' return a list with RA notes'''
        return self.notes

    def getGeneralInfo(self):
        ''' return a dictionary with RA status'''
        return {'general':self.general}

    def updateGeneralInfo (self, input):
        ''' process update as GeneralInfo when we are in the first step'''
        if not 'general' in input:
            return False, 'wrong format in input file (no "general" info)'

        self.general = input['general']

        # if workflow_custom... copy to repo and replace workflow.csv
        if 'workflow_custom' in self.general:
            workflow_custom = self.general['workflow_custom']
            if workflow_custom is not None:
                if os.path.isfile(workflow_custom):
                    shutil.copy(workflow_custom,self.rapath)
                    self.ra['workflow_name'] = workflow_custom
                    LOG.debug (f'workflow name updated to {workflow_custom}')

        self.workflow = Workflow(self.raname, self.ra['workflow_name'])

        # set firstnode as active node
        active_node = self.workflow.firstNode()
        self.ra['active_nodes_id']=[active_node.getVal('id')]
        LOG.info(f'active node updated to: {self.ra["active_nodes_id"]}' )

        # advance workflow: we are in step 0, move to step 1
        LOG.info(f'workflow advanced to step: {1}')
        self.ra['step']=1

        self.save()

        return True, 'OK'

    def update(self, input):
        ''' validate result and if it matchs the requirements of an active node progress in the workflow'''

        # validate result
        step = self.ra['step']

        # special case of the first step
        if step == 0:
            return self.updateGeneralInfo(input)
        
        if not 'result' in input:
            return False, 'wrong format in input file (no "result" info)'
        
        # the input file can contain a list of results, consider one by one
        for input_result in input['result']:
            
            # identify the node for which this result has been obtained
            input_node_id = input_result['id']

            # validate input, the template must be tagged for this workflow node
            if not input_node_id in self.ra["active_nodes_id"]:
                LOG.info(f'input for node {input_node_id} not in the active nodes list({self.ra["active_nodes_id"]})')
                continue
            
            # identify workflow node for which this result is being applied
            input_node = self.workflow.getNode(input_node_id)
            input_node_cathegory = input_node.getVal('cathegory')

            # if node is empty do not process and do not progress in workflow
            if input_node_cathegory == 'LOGICAL':
                if not 'decision' in input_result:
                    continue
                if type(input_result['decision']) != bool:
                    LOG.info (f'result for node {input_node_id} empty')
                    continue

            elif input_node_cathegory == 'TASK':
                if not 'value' in input_result:
                    continue
                if input_result['value'] is None:
                    LOG.info (f'result for node {input_node_id} empty')
                    continue

            # append result
            self.results.append(input_result)

            # if update contains links to local files, upload to repository
            # if 'result_link' in input_result:
            #     link = input_result['result_link']
            #     if link is not None:
            #         if os.path.isfile(link):
            #             hist_dir = os.path.join(self.rapath, 'repo')
            #             try:
            #                 shutil.copy(link, hist_dir)
            #             except Exception as err:
            #                 LOG.error(f'error: {err}, file {link} not processed')

            # replace the current node with the next for the current node only 
            # if logical find new active node (method in workflow?)
            active_nodes_list = self.ra['active_nodes_id']
            active_nodes_list.pop(active_nodes_list.index(input_node_id))

            if input_node_cathegory == 'LOGICAL':
                new_nodes_list = self.workflow.logicalNodeList(input_node_id, input_result['decision'])
                self.ra['active_nodes_id'] = active_nodes_list + new_nodes_list
                LOG.info(f'active node updated to: {self.ra["active_nodes_id"]}, based on decision {input_result["decision"]}' )

            elif input_node_cathegory == 'TASK':
                new_nodes_list= self.workflow.nextNodeList(input_node_id)
                self.ra['active_nodes_id'] = active_nodes_list + new_nodes_list
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

    def getWorkflowGraph(self):
        return 'xxxx'
           
    #################################################
    # output section
    #################################################

    def getTemplate (self):
        ''' dumps a template of the results for the following active nodes
        '''
        current_step = self.ra['step']
        results = f'# template for step {current_step}\n'
        if current_step == 0:
            results+= yaml.dump({'general':self.general})
        else:
            result_labels = '# input needed for the following nodes\n'
            result_list = []
            for iid in self.ra['active_nodes_id']:
                inode = self.workflow.getNode(iid)
                result_labels+= f'# node {inode.getVal("name")}\n'

                itask = inode.getTask()
                result_list.append(itask.getTemplateDict()['result'])
                # iresult= itask.getTemplateDict()
            
            results = result_labels + yaml.dump ({'result':result_list})

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

    def checkStep (self, dict, step):
        ''' convenience function to check if a dictionary descrives the given step'''
        if 'ra' in dict:
            if 'step' in dict['ra']:
                if dict['ra']['step'] == step:
                    return True
        return False
