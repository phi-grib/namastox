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
from namastox.task import Task

LOG = get_logger(__name__)

class Node:
    ''' Class representing a workflow node
    '''
    # def __init__(self, node_name, node_id, node_type, node_task=None):
    def __init__(self, node_content):
        ''' constructor '''
        self.name = node_content['name']
        self.id = node_content['id']
        self.category = node_content['category']
        self.next_node = node_content['next_node']
        self.next_yes = node_content['next_yes']
        self.next_no = node_content['next_no']
        self.setTask(node_content)
    
    def getVal(self, field):
        if field in self.__dict__:
            return self.__dict__[field]
        return None
    
    def nextNodeIndex(self):
        index_str = self.next_node 
        
        if index_str is None:
            return []
        
        index_list = [(int(x)-1) for x in index_str.split(',')] 
        return (index_list)

    def logicalNodeIndex(self, decision):
        if decision:
            index_str = str(self.next_yes) 
        else:
            index_str = str(self.next_no) 
        
        if index_str is None:
            return []

        index_list = [(int(x)-1) for x in index_str.split(',')] 
        return (index_list)
    
    def setTask(self, node_task):
        self.task = Task(node_task)

    def getTask(self):
        task = None
        task = self.task
        return task
    
    def style (self, visited=False, future=False):
        # color of next nodes
        if future:
            return f'style {self.id} fill:#e9f5f9,stroke:#a8d5e5\n'
        
        # color of visited nodes
        if visited:
            return f'style {self.id} fill:#DDDDDD,stroke:#DDDDDD\n'
        
        # color of terminao nodes
        if self.category == 'END':
            return f'style {self.id} fill:#FFFFFF,stroke:#000000\n'

        # color of visited nodes
        return f'style {self.id} fill:#78A4DE,stroke:#6697d9\n'
        
        # if self.category == 'TASK' :
        #     return f'style {self.id} fill:#78A4DE,stroke:#6697d9\n'
        # if self.category == 'LOGICAL':
        #     return f'style {self.id} fill:#78A4DE,stroke:#6697d9\n'
        #     # return f'style {self.id} fill:#548BD4,stroke:#548BD4\n'
        #     # return f'style {self.id} fill:#F2DCDA,stroke:#C32E2D\n'
        # return '\n'
    
    def box (self):
        if self.category == 'TASK':
            return f'{self.id}[{self.name}]'
        if self.category == 'LOGICAL':
            return f'{self.id}{{{self.name}}}'
        if self.category == 'END':
            return f'{self.id}[/{self.name}/]\n{self.id}[/{self.name}/]-->Z[end]'
        return ''
        