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
        This class represents only the *topological aspects* of the node
        All the data is in class Task (results)
    '''
    def __init__(self, node_content):
        ''' constructor '''
        self.name = node_content['name']
        self.id = node_content['id']
        self.category = node_content['category']

        self.next_node = []
        if isinstance(node_content['next_node'], str):
            node_list = node_content['next_node'].replace(' ','').split(',')
            self.next_node = node_list

        self.next_yes = []
        if isinstance(node_content['next_yes'], str):
            node_list = node_content['next_yes'].replace(' ','').split(',')
            self.next_yes = node_list

        self.next_no = []
        if isinstance(node_content['next_no'], str):
            node_list = node_content['next_no'].replace(' ','').split(',')
            self.next_no = node_list

        self.setTask(node_content)
    
    def getVal(self, field):
        if field in self.__dict__:
            return self.__dict__[field]
        return None
    
    def nextNodes(self):
        return self.next_node
    
    def nextLogicalNodes (self, decision):
        if decision:
            return self.next_yes
        else:
            return self.next_no
   
    def setTask(self, node_task):
        self.task = Task(node_task)

    def getTask(self):
        task = None
        task = self.task
        return task

    def styleClass (self, visited=False, future=False):
        # terminal nodes
        if self.category == 'END':
            return ('znode')
        
        # workflow node
        # SOLVE!
        # if self.id[0] == 'W':
        #     print ('**********************', self.id)
        #     return ('wnode')
        
        # next nodes
        if future:
            return('fnode')       
        
        # visited nodes
        elif visited:
            return('vnode')
        
        # active nodes
        else:
            return('anode')

    def box (self):
        # split labels in half, adding '\\n' betweeen the two middle words
        words = self.name.split()
        label = ''
        for i,iword in enumerate(words):
            label += iword
            if i == round(len(words)/2.0)-1:
                # label += '\\n'
                label += '<br>'
            else:
                label += ' '

        if self.category == 'TASK':
            return f'{self.id}[{label}]'
        if self.category == 'LOGICAL':
            return f'{self.id}{{{label}}}'
        if self.category == 'END':
            return f'{self.id}[/{self.name}/]\n{self.id}[/{self.name}/]-->Z{self.id}[end]'
        return ''
        