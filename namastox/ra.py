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
from namastox.task import Task
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
        
        # default, these are loaded from a YAML file
        self.ra = {
            'ID': None,
            'workflow_name': None,
            'step': 0,
            'active_nodes_id': [],
            'tasks_completed': None,
            'notes': None
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
        # self.assessment = None
        self.placehoders = {
            'general_description': 'Descriptive text about this study',
            'background': 'Any relevant information',
            'endpoint': 'Toxicological endpoint(s) of interest',
            'title': 'Descriptive name for this study',
            'problem_formulation': 'Short description of the toxicological issue to be adressed',
            'uncertainty': 'Comments about the acceptable uncertainty levels', 
            'administration_route': 'Administration routes of the toxican to be considered',
            'species': 'Biological species to be considered',
            'regulatory_framework': 'Regulatory bodies for which this study can be of interest',
            'workflow_custom': 'File describing the workflow. If empty the ASPA workflow will be used instead',
            'substances': {
                'name': ' Substance name or names separated by a colon',
                'id': ' Substance ID or IDs separated by a colon',
                'casrn': ' Substance CAS-RN or CAS-RNs separated by a colon',
            }
        }
        self.users_read = []
        self.users_write = []
        
        self.loadUsers()


    def privileges(self, username):
        priv = ''
        if username in self.users_read:
            priv+='r'
        elif '*' in self.users_read:
            priv+='r'
        if username in self.users_write:
            priv+='w'
        elif '*' in self.users_write:
            priv+='w'

        return priv

    def getUsers(self):
        ''' get the 
        '''
        return {'read':self.users_read, 'write':self.users_write}
    
    def setUsers(self, username_read, username_write):
        ''' sets the RA list of users and save it to a users.pkl file
        '''
        self.users_read = username_read
        self.users_write = username_write
        if os.path.isdir (self.rapath):
            users_file = os.path.join (self.rapath,'users.pkl')
            with open (users_file,'wb') as handle:
                pickle.dump(self.getUsers(), handle)

    def loadUsers(self):
        ''' load user information from users.pkl file
        '''
        if os.path.isdir (self.rapath):
            users_file = os.path.join (self.rapath,'users.pkl')
            if os.path.isfile (users_file):
                with open (users_file,'rb') as handle:
                    users_dict = pickle.load(handle)
                    self.users_read = users_dict['read']
                    self.users_write = users_dict['write']

            # for legacy compatibilit, when no users.pkl file is found
            else:
                LOG.info(f'applying legacy user patch for RA {self.raname}')

                with open (users_file,'wb') as handle:
                    pickle.dump({'read':["*"], 'write': ["*"]}, handle)
                    self.users_read = '*'
                    self.users_write = '*'
    

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
            return False, f'error:{e}'
        
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
        keylist = ['ra', 'general', 'results', 'notes']
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
            'notes': self.notes
        }
        with open(rafile,'w') as f:
            f.write(yaml.dump(dict_temp))

        # rename other yaml file in the historic describing the same step as bk_
        step = self.ra['step']
        
        files_to_rename = []

        rahistpath = os.path.join (self.rapath,'hist')

        for ra_hist_file in os.listdir(rahistpath):
            if not ra_hist_file.startswith('ra_'):
                continue
            ra_hist_item = os.path.join(rahistpath, ra_hist_file)
            if os.path.isfile(ra_hist_item):
                idict = {}
                with open(ra_hist_item, 'r') as pfile:
                    idict = yaml.safe_load(pfile)
                    if 'ra' in idict:
                        if 'step' in idict['ra']:
                            if step == idict['ra']['step']:
                                files_to_rename.append(ra_hist_file)

            for ifile in files_to_rename:
                ipath = os.path.join(rahistpath,ifile)
                if os.path.isfile(ipath):
                    bk_name = os.path.join(rahistpath, 'bk_'+ ifile[3:])
                    i=1
                    while os.path.isfile(bk_name):
                        bk_name = os.path.join(rahistpath, f'bk_{ifile[3:-5]}_{str(i)}.yaml')
                        i=i+1
                    os.rename(ipath, bk_name)

        # save in the historic file
        time_label = time.strftime("_%d%b%Y_%H%M%S", time.localtime()) 
        rahist = os.path.join (rahistpath,f'ra{time_label}.yaml')
        shutil.copyfile(rafile, rahist)

    def getStatus(self):
        ''' return a dictionary with RA status
        '''

        # Update the number of tasks completed and the number of notes
        self.ra['tasks_completed'] = len (self.results)
        self.ra['notes'] = len (self.notes)

        return {'ra':self.ra}

    def getActiveNodes (self):
        ''' returns a list with the active nodes
        '''
        active_nodes_id = self.ra['active_nodes_id']
        olist = []
        
        if active_nodes_id is None:
            return olist

        for node_id in active_nodes_id:
            input_node = self.getNode(node_id)
            itask = input_node.getTask()
            olist.append({'id':node_id, 
                          'label':itask.getLabel(),
                          'name':itask.getName(),
                          'description':itask.getDescriptionText(),
                          'category':itask.getCategoryText()})
        return olist
    
    def getActiveNode (self, node_id):
        ''' return a dictionary with the task description of the node_id given as argument,
            but only if this discribes an active node
        '''
        active_nodes_id = self.ra['active_nodes_id']
        if node_id in active_nodes_id:
            input_node = self.getNode(node_id)
            itask = input_node.getTask()
            return (itask.getDescriptionDict())
        return None

    def getUpstreamNodes (self, node_id):
        ''' returns a list with nodes upstream to the node_id provided as argument
            this is ONLY for decision nodes, but no checking is performed for now

        '''
        olist = []

        upstream_nodes_id = self.workflow.getUpstreamNodes (node_id)

        for node_id in upstream_nodes_id:

            # skip non-visited nodes
            if not self.workflow.isVisitedNode(node_id, self.results):
                continue

            input_node = self.getNode(node_id)
            itask = input_node.getTask()

            # the content of the nodes (values, uncertainties) is extracted
            # from self.results
            ivalue = []
            iuncertainties = []
            imethods = []
            for iresult in self.results:
                if iresult['id'] == node_id:
                    ivalue = iresult['values']
                    iuncertainties = iresult['uncertainties']
                    if 'methods' in iresult:
                        imethods = iresult['methods']
                    break

            # the name of the node is extracted from the itask description 
            olist.append({'id':node_id, 
                          'label':itask.getLabel(),
                          'name':itask.getName(),
                          'values':ivalue,
                          'uncertainties':iuncertainties,
                          'methods':imethods
                          })
        return olist

    def getResults(self):
        ''' return a list with RA results
        '''
        temp = []
        for iresult in self.results:
            # enrich the results by adding the name of the task
            iresult['name'] = self.workflow.getTaskName(iresult['id']) 
            temp.append(iresult)
        return temp

    def getResult(self, resultid):
        ''' return the RA result with ID as the one provided as argument
        '''
        for iresult in self.results:
            if iresult['id'] == resultid:
                # enrich the results by adding the name of the task
                iresult['name'] = self.workflow.getTaskName(resultid)
                return iresult
        return None
    
    def getTask(self, result_id):
        ''' utility funcion to obtain the Task with the result_id given as argument
            note that we extract the task description from the workflow and add the results from
            the internal result list
        '''
        itask = self.workflow.getTask(result_id)
        if itask == None:
            return None
        icombo = itask.getDescriptionDict()

        found = False
        for iresult in self.results:
            if iresult['id'] == result_id:
                found = True
                icombo['result'] = iresult

        if not found:
            return None        

        return icombo
    
    def getNode(self, result_id):
        '''utility funcion to obtain the node with the result_id given as argument
        '''
        return self.workflow.getNode(result_id)

    def getNotes(self):
        ''' return a list with RA notes
        '''
        return self.notes
    
    def addNote(self, note):
        ''' append the note give as argument to the RA notes
        '''
        self.notes.append(note)
        self.ra['notes'] = len (self.notes)
        return True

    def getGeneralInfo(self):
        ''' return a dictionary with RA status
        '''
        return {'general':self.general, 
                'placeholders':self.placehoders}

    def updateGeneralInfo (self, input):
        ''' process update as GeneralInfo when we are in the first step (step 0)
        '''
        if not 'general' in input:
            return False, 'wrong format in input file (no "general" info)'

        self.general = input['general']

        # if we are aditing an existing RA, simply return
        if self.ra['step']>0:
            LOG.info('Existing general info has been updated')
            return True, 'Update OK'
        
        # if we are defining the General Info for the first time...

        # process any custom workflow
        if 'workflow_custom' in self.general:
            workflow_custom = self.general['workflow_custom']

            if workflow_custom is not None:
                if os.path.isfile(os.path.join(self.rapath,workflow_custom)):
                    
                    self.ra['workflow_name'] = workflow_custom
                    workflow_pkl = os.path.join(self.rapath,'workflow.pkl')
                    if os.path.isfile(workflow_pkl):
                        os.remove(workflow_pkl)
                        
                    LOG.info (f'workflow name updated to {workflow_custom}')

        self.workflow = Workflow(self.raname, self.ra['workflow_name'])

        # set firstnode as active node
        active_node = self.workflow.firstNode()
        self.ra['active_nodes_id']=[active_node.getVal('id')]
        LOG.info(f'active node updated to: {self.ra["active_nodes_id"]}' )

        # advance workflow: we are in step 0, move to step 1
        LOG.info('workflow advanced to step: 1')
        self.ra['step']=1

        # DO NOT SAVE HERE! this is called by update.py and it will be saved from there
        # self.save()

        return True, 'OK'

    def append_result (self, input_result):
        ''' utility function used by update
            used when the input_result will apply to a terminal node (active node) and 
            therefore will expand the workflow
        '''

        # identify workflow node for which this result is being applied
        input_result_id = input_result['id']
        input_node = self.getNode(input_result_id)
        input_node_category = input_node.getVal('category')

        self.results.append(input_result)

        active_nodes_list = self.ra['active_nodes_id']

        # remove current node from the list of actives
        active_nodes_list.pop(active_nodes_list.index(input_result_id))

        # get new nodes which will become active afther this action
        new_nodes_list = []
        if input_node_category == 'LOGICAL':
            new_nodes_list = self.workflow.logicalNodeList(input_result_id, input_result['decision'])
        elif input_node_category == 'TASK':
            new_nodes_list = self.workflow.nextNodeList(input_result_id)

        # clean visited nodes
        for inew_node in new_nodes_list:
            if self.workflow.isVisitedNode(inew_node, self.results):
                new_nodes_list.pop(new_nodes_list.index(inew_node))

        # merge, remove duplicates and sort to present the list in an ordered and reproducible way
        new_active_nodes_list = sorted(list(set(active_nodes_list + new_nodes_list)))

        # update the active nodes list
        self.ra['active_nodes_id'] = new_active_nodes_list

        LOG.info(f'active node updated to: {self.ra["active_nodes_id"]}' )

        # advance workflow: step+1, active workflow+1
        step = self.ra['step']
        self.ra['step']=step+1
        self.ra['tasks_completed'] = len(self.results)
        LOG.info(f'workflow advanced to step: {step+1}')

    def edit_result (self, input_result):
        ''' utility function used by update
            used when the input result is an already existing node and we only want to update its contents
            decisions cannot be edited to change their value
        '''
        input_result_id = input_result['id']
        input_node = self.getNode(input_result_id)
        input_node_category = input_node.getVal('category')
 
        for i, iresult in enumerate(self.results):
            if iresult['id'] == input_result_id:

                # for now, decisions cannot be ammended
                if input_node_category == 'LOGICAL':
                    if input_result['decision']!=self.results[i]['decision']:
                        LOG.info (f'decisions cannot be ammended')
                        return

                self.results[i] = input_result
            LOG.info(f'result {i} updated successfully')

    def update(self, input):
        ''' validate result and if it matchs the requirements of an active node progress in the workflow
        '''

        step = self.ra['step']

        # special case of the first step
        if step == 0:
            return self.updateGeneralInfo(input)
        
        if not 'result' in input:
            return False, 'wrong format in input file (no "result" info)'
        
        # the input file can contain a list of results, consider one by one
        for input_result in input['result']:
            
            # identify the node for which this result has been obtained
            input_result_id = input_result['id']
            
            # get the type of node
            input_node = self.getNode(input_result_id)
            input_node_category = input_node.getVal('category')

            # add the label to the input result
            input_result['label'] = input_node.getTask().getLabel()
            
            # if node is empty do not process and do not progress in workflow
            if input_node_category == 'LOGICAL':
                if not 'decision' in input_result:
                    continue

                if type(input_result['decision']) != bool:
                    LOG.info (f'result for node {input_result_id} empty')
                    continue
                
            elif input_node_category == 'TASK':
                if not 'values' in input_result:
                    continue
                
                values_list = input_result['values']

                if len(values_list)==0:
                    LOG.info (f'result for node {input_result_id} empty')
                    continue

                # remove empty items from value list and, if present, from
                # uncertainties list as well
                if 'uncertainties' in input_result:
                    uncert_list = input_result['uncertainties']
        
                    for ival, iunc in zip(values_list, uncert_list):
                        if ival == {}:
                            values_list.remove(ival)
                            uncert_list.remove(iunc)
                else:
                    for ival in values_list:
                        if ival == {}:
                            values_list.remove(ival)

            
            # if this result is for an active node APPEND the information
            if input_result_id in self.ra["active_nodes_id"]:
                self.append_result(input_result)
            else:
                self.edit_result(input_result)

            input_result['date']= time.strftime("%d/%b/%Y %H:%M", time.localtime()) 


        # DO NOT SAVE HERE! this is called by update.py and it will be saved from there
        # self.save()

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

    def getWorkflowGraph(self, step=None):
        ''' returns a mermaid graph for the workflow, util the step given as argument
            if the ra is in step 0 and the workflow is still undefined, return a fallback graph 
        '''
        if self.ra['step']>0 : 
            print (self.workflow.getWorkflowGraph(self.workflow.catalogue))    
            # return self.workflow.getWorkflowGraph(self.results, step)    
            return self.workflow.getWorkflowGraph(self.workflow.catalogue, step)    
         
        return """graph TD
                  X[workflow undefined]-->Z[...]
                  style X fill:#548BD4,stroke:#548BD4
                  style Z fill:#FFFFFF,stroke:#000000
                  """
    
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
                inode = self.getNode(iid)
                result_labels+= f'# node {inode.getVal("name")}\n'

                itask = inode.getTask()
                result_list.append(itask.getTemplateDict()['result'])
            
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
