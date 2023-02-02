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
from src.task import Task

LOG = get_logger(__name__)

class Node:
    ''' Class representing a workflow node
    '''
    def __init__(self, node_name, node_id, node_type, node_task=None):
        ''' constructor '''
        self.name = node_name
        self.id = node_id
        self.type = node_type
        self.task = None        
        if node_task != None:
            self.setTask(node_task)

        # print ('>>>', self.id, self.name, self.type)

    def getVal(self, field):
        if field in self.__dict__:
            return self.__dict__[field]
        return None
    
    def setTask(self, node_task):
        self.task = Task(node_task)

    def getTask(self):
        return self.task()
        
    def getTaskVal(self, field):
        if field in self.task:
            return self.task[field]
        return None