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

# import yaml
import os
import sys
import pickle
import pandas as pd
import numpy as np
from namastox.utils import ra_path
from namastox.node import Node
from namastox.logger import get_logger
from namastox.node import Node

LOG = get_logger(__name__)

class Workflow:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self, raname, workflow=None):
        ''' constructor '''
        if workflow is not None:
            self.workflow = workflow
        else:
            self.workflow = 'workflow.csv'

        self.nodes = []
        self.rapath = ra_path(raname)

        success = self.load()
        if not success:
            success = self.import_table()

        if not success:
            LOG.error('CRITICAL: unable to load a correct workflow definition')
            sys.exit(-1)

    def import_table (self):
        table_path = os.path.join (self.rapath,self.workflow)
        
        LOG.debug (f'import table {table_path}')

        table_dataframe = pd.read_csv(table_path, sep='\t').replace(np.nan, None)
        table_dict = table_dataframe.to_dict('list')

        index_labels = ['id', 'name', 'cathegory', 'next_node', 'next_yes', 'next_no']
        for i in index_labels:
            if not i in table_dict:
                return False

        for i in range(table_dataframe.shape[0]):
            node_content = {}
            for key in table_dict:
                value = table_dict[key][i] 
                if key in ['next_node', 'next_yes', 'next_no']:
                    if type(value) == float:
                        value = int(value)
                node_content[key]=value   
            self.nodes.append(Node(node_content))
             
        self.save()

        return True
         
    def load(self):       
        ''' load the Expert object from a pickle
        '''
        pickl_path = os.path.join (self.rapath,'workflow.pkl')

        if not os.path.isfile(pickl_path):
            return self.import_table()
        
        with open(pickl_path,'rb') as f:
            self.nodes = pickle.load(f)
            
        return True

    def save (self):
        ''' saves the Expert object to a pickl
        '''
        pickl_path = os.path.join (self.rapath,'workflow.pkl')
        with open(pickl_path,'wb') as f:
            pickle.dump(self.nodes, f, protocol=pickle.HIGHEST_PROTOCOL)

    def getNode (self, iid):
        for inode in self.nodes:
            if inode.getVal('id') == iid:
                return inode
            
    def firstNode (self):
        return self.nodes[0]
    
    def nextNodeList (self, iid):
        inode = self.getNode(iid)
        index_list = inode.nextNodeIndex()
        return [self.nodes[x].getVal('id') for x in index_list]

    def logicalNodeList (self, iid, decision):
        inode = self.getNode(iid)
        index_list = inode.logicalNodeIndex(decision)        
        return [self.nodes[x].getVal('id') for x in index_list]
    
    def getWorkflowGraph (self, node_path):

        print ('WORKFLOW>>>>>', node_path)
        header = 'graph TD\n'

        body = ''
        for iid in node_path:
            inode = self.getNode(iid)
            if inode.cathegory == 'TASK':
                next_nodes = self.nextNodeList(iid)
                for jid in next_nodes:
                    inext = self.getNode(jid)
                    body += f'{inode.id}[{inode.name}]-->{inext.id}[{inext.name}]\n'
            elif inode.cathegory == 'LOGICAL':
                next_nodes =self.logicalNodeList(iid)
                for jid in next_nodes:
                    inext = self.getNode(jid)
                    body += f'{inode.id}[{inode.name}]-->{inext.id}[{inext.name}]\n'

        print (body)

        w = """graph TD
        A[Problem formulation]-->B[Relevant existing data]
        B-->C{"Is the information\nsufficient?"}
        C--Y-->D[/Risk assesment report/]
        C--N-->E{"Is exposure scenario\nwell-defined?"}
        E---G[...]
        D-->F([Exit])
        style A fill:#548BD4,stroke:#548BD4
        style B fill:#548BD4,stroke:#548BD4
        style C fill:#F2DCDA,stroke:#C32E2D
        style E fill:#F2DCDA,stroke:#C32E2D
        style F fill:#D7E3BF,stroke:#A3B77E
        style G fill:#FFFFFF,stroke:#000000
        click A onA
        click B onA
        click C onA
        click D onA
        click E onA"""
                
        return w





   