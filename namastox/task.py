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
            'area': None,            # TODO: remove 

            'decision': 'Select yes or no to the question posed in the description',       
            'report': 'Text report with the main conclussions of the task',         
            'unit': 'Units of the value (e.g., mg/K)', # deprecated            
            'value': 'Enter a numerical value (as a floating point) with the result of the task', # deprecated          
            'values': 'Enter one or many numerical parameters, consisting in a description, value (as a floating point) and unit',          
            'uncertainty': 'Information about the uncertainty associated to the value',     
            'summary': 'Short description of the results',
            'result_link': 'Link any relevant document in PDF format'     
        }

        self.result = {
            # move to description ###################################
            'id': None,
            'result_type': None,     # text | value | bool
            #######################################
            
            'substance': None,       # TODO: remove

            'decision': False,       # for LOGICAL tasks
            'report': False,         # for result_type = text
            'values': [],            # list of values {
                                     #  'parameter': 'pKa',
                                     #  'value': 0.18,
                                     #  'unit': 'nM',
                                     # }
            'value': None,           # for result_type = value *** DEPRECATED ***
            'unit': None,            # for result_type = value *** DEPRECATED ***
            'uncertainty': None,     # for result_type = value 
            'summary': None,
            'result_link': None      # TODO: should be a list
        }

        self.other = {}
        self.setTask(task_dict)

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

    def setTask(self, task_dict):
        '''parses the input dictionary and assign contents for description and results
           this functions is typically called when parsing the table with the workflow
        '''
        for ikey in self.description:
            if ikey in task_dict:
                self.description[ikey]=task_dict[ikey]

        for ikey in self.result:
            if ikey in task_dict:
                self.result[ikey]=task_dict[ikey]

        for ikey in task_dict:
            if ikey not in self.result and ikey not in self.description:
                self.other[ikey]=task_dict[ikey]

    def setResult(self, result_dict):
        for ikey in self.result:
            if ikey in result_dict:
                self.result[ikey]=result_dict[ikey]

    # UTILS
    def getResult (self, category):
        temp_result = self.result.copy()
        if category == 'TASK':
            temp_result.pop ('decision')
        elif category == 'LOGICAL':
            temp_result.pop ('report')
            temp_result.pop ('values')
            temp_result.pop ('value')
            temp_result.pop ('unit')
            temp_result.pop ('uncertainty')
        return temp_result

    def valResult(self, task_result):
        ''' makes sure that the task_result dict meets the task requirements
        '''

        if type(task_result) is not dict:
            return False

        compulsory_keys = ['substance', 'summary']

        if self.description['category'] == 'LOGICAL':
            compulsory_keys.append ('decision')
        elif self.description['category'] == 'TASK':
            compulsory_keys.append ('report')
            compulsory_keys.append ('value')
            # compulsory_keys.append ('values')
            compulsory_keys.append ('unit')
            compulsory_keys.append ('uncertainty')

        for ikey in compulsory_keys:
            if ikey not in task_result:
                return False

        return True