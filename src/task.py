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

from src.logger import get_logger
import yaml

LOG = get_logger(__name__)

# Description
#    cathegory: [NAM|exposure|expert|decision]
#    description:
#    link_method:

# Result template
#    substance : example
#    summary: 
#    value: 
#    unit:
#    uncertainty:
#    link_result : exposure_study_for_example.xlxs


class Task:
    ''' Class representing a task associade to a workflow node
    '''

    def __init__(self, task_dict:dict=None):
        ''' constructor '''

        self.description = {
            'cathegory': 'TASK',
            'area': None,
            'description': None, 
            'method_type': 'expert', # expert, NAM, in silico, 
            'method_link': None 
        }

        self.result = {
            'id': None,
            'substance': None,
            'resul_description': 'text', # text, bool
            'resul_type': None, # text, bool
            'summary': None,
            'summary_type': 'text',  # text, bool, value, 'done'
            'value': None, 
            'unit': None,
            'uncertainty': None,
            'decision': False,
            'result_link': None
        }
        self.other = {}
        self.setTask(task_dict)

        # print ('+++', self.description, self.result)

    def getDescription(self):
        ''' generates a yaml with information for the end-user, describing what should be done
            - type of task
            - description
            - link to NAM method database
            - empty result template
        '''
        return yaml.dump({'task description':self.description, 'result':self.result})
    
    def getTemplate(self):
        '''generates a YAML for entering the results'''
        return yaml.dump ({'result':self.result})
    
    def valResult(self, task_result):
        ''' makes sure that the task_result dict meets the task requirements
        '''

        if type(task_result) is not dict:
            return False

        compulsory_keys = ['substance', 'summary']

        if self.description['cathegory'] == 'LOGICAL':
            compulsory_keys.append ('decision')
        elif self.description['cathegory'] == 'TASK':
            compulsory_keys.append ('value')
            compulsory_keys.append ('unit')

        for ikey in compulsory_keys:
            if ikey not in task_result:
                return False

        return True

    def setTask(self, task_dict):
        for ikey in self.description:
            if ikey in task_dict:
                self.description[ikey]=task_dict[ikey]

        for ikey in self.result:
            if ikey in task_dict:
                self.result[ikey]=task_dict[ikey]

        for ikey in task_dict:
            if ikey not in self.result and ikey not in self.description:
                self.other[ikey]=task_dict[ikey]