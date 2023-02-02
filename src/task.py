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

LOG = get_logger(__name__)

#    cathegory: [NAM|exposure|expert|decision]
#    substance : example
#    summary: 
#    value: 
#    unit:
#    uncertainty:
#    link : exposure_study_for_example.xlxs

class Task:
    ''' Class representing a task associade to a workflow node
    '''
    def __init__(self, task_dict:dict=None):
        ''' constructor '''

        # task_dict must contain information about 
        # 1. the task that the end-user must carry out 
        # 2. the result that is expected

        self.cathegory = None
        self.description = None
        self.method_link = None

        self.result = None


    def getDescription(self):
        ''''generates a yaml with information for the end-user, describing what should be done
            - type of task
            - description
            - link to NAM method database
            - empty result template
        '''
        return 'I am the result'
    
    def valResult(self):
        return True
