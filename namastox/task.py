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

from namastox.logger import get_logger
import yaml

LOG = get_logger(__name__)

class Task:
    ''' Class representing a task associade to a workflow node
        Everything related with the topological aspects of the task is
        represented by class Node
    '''

    def __init__(self, task_dict:dict=None):
        ''' constructor '''

        self.description = {
            'name': None,
            'id': None,
            'label': None,
            'result_type': None,     # text | value | bool
            'category': 'TASK',      # TASK | LOGICAL | END
            'description': None,     # cannot be left empty
            'method_type': 'expert', # expert | invitro | insilico, 
            'method_link': None,     # link to method repo

            'decision': 'Select yes or no to the question posed in the description',       
            'report': 'Text report with the main conclusions of tasks or justification for decisions',            
            'values': 'Enter one or many numerical parameters, consisting in a description, value (as a floating point) and unit',          
            'justification': 'Text providing a detailed justification of the decision taken', 
            'uncertainties':  'Enter uncertainty information about this task, including a textual description, a probability value and a descriptive term',         
            
            'uncertainty': 'Information about the uncertainty associated to the result',         # DEPRECATED
            'uncertainty_term': ['Almost certain (0.99-1.00)',                                   # DEPRECATED
                                 'Extremely likely (0.95-0.99)',
                                 'Very likely (0.90-0.95)',
                                 'Likely (0.66-0.90)',
                                 'About as likely as not (0.33-0.66)',
                                 'Unlikely (0.10-0.33)',
                                 'Very unlikely (0.05-0.10)',
                                 'Extremely unlikely (0.01-0.05)',
                                 'Almost impossible (0.00-0.01)'],
            'uncertainty_p': 'Uncertainty of result, as probability of being true, from 0 to 1', # DEPRECATED    

            'summary': 'Short description of the results',
            'links': 'Link any relevant document in PDF format'     
        }

        # The content of self.result is ONLY used to generate empty templates. Results are NOT stored here, but in ra.results[]
    
        self.result = {
            # move to description ###################################
            'id': None,
            'result_type': None,     # text | value | bool
            #########################################################
            # for LOGICAL
            'decision': False,       
            'justification': None,   
            
            # for TASK

            'report': False,         # for result_type = text

            'values': [],            # for result_type = report
                                     # list of values {
                                     #  'parameter': 'pKa',
                                     #  'value': 0.18,
                                     #  'unit': 'nM',
                                     # }

            # 'uncertainty': [],     
            # 'uncertainty_term': [],
            # 'uncertainty_p': [],   

            'uncertainties': [],     # list of values {
                                     #  'uncertainty': 'experimental SEM +/- 0.34',
                                     #  'p' : 0.99
                                     #  'term' : 'Very likely'
                                     # }
            
            # for ALL
            'date': None,
            'summary': None,
            'links': [],             # list of link names and files {
                                     #   'result_name' : 'in-silico predicton using model XGSHAT3 ',
                                     #   'result_link' : 'report.pdf'  
                                     # }
        }

        self.other = {}
        self.setTask(task_dict)

    def getName (self):
        '''returns the task name field'''
        if not 'name' in self.description:
            return None
        return (self.description['name'])
    
    def getLabel (self):
        '''returns the task label field'''
        if not 'label' in self.description:
            return None
        return (self.description['label'])
    
    def getDescriptionText (self):
        '''returns the task description field'''
        if not 'description' in self.description:
            return None
        return (self.description['description'])

    def getCategoryText (self):
        '''returns the task category field'''
        if not 'category' in self.description:
            return None
        return (self.description['category'])

    def getDescriptionDict(self):
        ''' generates a yaml with information for the end-user, describing what should be done
            - type of task
            - description
            - link to NAM method database
            - empty result template
        '''
        return {'task description':self.description, 
                'result':self.getResult(self.description['category'])}
    
    def getDescription(self):
        ''' generates a yaml with information for the end-user, describing what should be done
            - type of task
            - description
            - link to NAM method database
            - empty result template
        '''
        return yaml.dump({'task description':self.description, 
                          'result':self.getResult(self.description['category'])})
    
    def getTemplateDict(self):
        '''returns the results dict for entering the results, adapted to the node category
        '''
        return {'result':self.getResult(self.description['category'])}

    def getTemplate(self):
        '''generates a YAML for entering the results'''
        return yaml.dump(self.getTemplateDict())

    def setTask(self, task_dict:dict):
        '''parses the input dictionary and assign contents for description and results
           this functions is typically called when parsing the table with the workflow
        '''
        for ikey in self.description:
            if ikey in task_dict:
                self.description[ikey]=task_dict[ikey]
                # print ('>>>>>',ikey, self.description[ikey])

        for ikey in self.result:
            if ikey in task_dict:
                self.result[ikey]=task_dict[ikey]

        for ikey in task_dict:
            if ikey not in self.result and ikey not in self.description:
                self.other[ikey]=task_dict[ikey]

    # def setResult(self, result_dict:dict):
    #     ''' sets the fields of the results dict provided in argument as fields of self.result'''
    #     for ikey in self.result:
    #         if ikey in result_dict:
    #             self.result[ikey]=result_dict[ikey]

    def getResult (self, category):
        ''' returns self.results, removing information for the type of task provided as argument'''
        temp_result = self.result.copy()
        
        black_keys=[]
        
        if category == 'TASK':
            black_keys = ['decision', 'justification']
        elif category == 'LOGICAL':
            black_keys = ['values']

        for bkey in black_keys:
            if bkey in temp_result:
                temp_result.pop (bkey)

        return temp_result

    # def valResult(self, task_result:dict):
    #     ''' makes sure that the task_result dict meets the task requirements
    #     '''
    #     if type(task_result) is not dict:
    #         return False

    #     compulsory_keys = ['summary']

    #     if self.description['category'] == 'LOGICAL':
    #         compulsory_keys.append ('decision')
    #         compulsory_keys.append ('justification')

    #     elif self.description['category'] == 'TASK':
    #         compulsory_keys.append ('report')
    #         compulsory_keys.append ('values')
    #         compulsory_keys.append ('uncertainties')
    #         # compulsory_keys.append ('uncertainty')
    #         # compulsory_keys.append ('uncertainty_term')
    #         # compulsory_keys.append ('uncertainty_p')

    #     for ikey in compulsory_keys:
    #         if ikey not in task_result:
    #             return False

    #     return True
        