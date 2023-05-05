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
            'cathegory': 'TASK',     # TASK | LOGICAL | END
            'description': None,     # cannot be left empty
            'method_type': 'expert', # expert | invitro | insilico, 
            'method_link': None,      # link to method repo
            'area': None            # TODO: remove 
        }

        self.result = {
            # move to description
            'id': None,
            'result_type': None,     # text | value | bool

            'substance': None,       # TODO: remove
            'decision': False,       # for LOGICAL tasks
            'report': False,         # for result_type = text
            'value': None,           # for result_type = value 
            'unit': None,            # for result_type = value 
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

    def getCathegoryText (self):
        '''returns the task cathegory field'''
        if not 'cathegory' in self.description:
            return None
        return (self.description['cathegory'])

    def getDescription(self):
        ''' generates a yaml with information for the end-user, describing what should be done
            - type of task
            - description
            - link to NAM method database
            - empty result template
        '''
        return yaml.dump({'task description':self.description, 
                          'result':self.getResult(self.description['cathegory'])})
    
    def getTemplateDict(self):
        '''returns the results dict for entering the results, adapted to the node cathegory
        '''
        return {'result':self.getResult(self.description['cathegory'])}

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

    # UTILS
    def getResult (self, cathegory):
        temp_result = self.result.copy()
        if cathegory == 'TASK':
            temp_result.pop ('decision')
        elif cathegory == 'LOGICAL':
            temp_result.pop ('report')
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

        if self.description['cathegory'] == 'LOGICAL':
            compulsory_keys.append ('decision')
        elif self.description['cathegory'] == 'TASK':
            compulsory_keys.append ('report')
            compulsory_keys.append ('value')
            compulsory_keys.append ('unit')
            compulsory_keys.append ('uncertainty')

        for ikey in compulsory_keys:
            if ikey not in task_result:
                return False

        return True