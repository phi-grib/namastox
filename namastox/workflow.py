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

        index_labels = ['id', 'label', 'name', 'category', 'next_node', 'next_yes', 'next_no']
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
        return None

    def getTask (self, iid):
        for inode in self.nodes:
            if inode.getVal('id') == iid:
                return inode.getTask()
        return None    
            
    def firstNode (self):
        return self.nodes[0]
    
    def nextNodeList (self, iid):
        inode = self.getNode(iid)
        index_list = inode.nextNodeIndex()
        return [self.nodes[x].getVal('id') for x in index_list]

    def logicalNodeList (self, iid, decision):
        inode = self.getNode(iid)
        index_list = inode.logicalNodeIndex(decision)   
        print ('index_list:', index_list)   
        print ('selfnodes len:', len(self.nodes))     

        return [self.nodes[x].getVal('id') for x in index_list]
    
    def graphNext (self, nodeid, inode, decision=None, visited=False):
        inext = self.getNode(nodeid)
        arrow = '-->'
        if decision is True:
            arrow = '--Y-->'
        elif decision is False:
            arrow = '--N-->'
        ibody = f'{inode.box()}{arrow}{inext.box()}\n'
        istyle = inext.style()
        ilinks = f'click {inext.id} onA\n'

        if inext.category == 'LOGICAL' and not visited:
            next_nodes_true  =self.logicalNodeList(nodeid, True)
            for jid in next_nodes_true:
                ilog = self.getNode(jid)
                ibody += f'{inext.box()}--Y-->{ilog.box()}\n'
                istyle += ilog.style(True)
                ilinks += f'click {ilog.id} onA\n'

            next_nodes_false  =self.logicalNodeList(nodeid, False)
            for jid in next_nodes_false:
                ilog = self.getNode(jid)
                ibody += f'{inext.box()}--N-->{ilog.box()}\n'
                istyle += ilog.style(True)
                ilinks += f'click {ilog.id} onA\n' 
             
        return ibody, istyle, ilinks
        

    def getWorkflowGraph (self, results, step=None):

        node_path =[iresult['id'] for iresult in results]

        header = 'graph TD\n'
        body = ''
        style = ''
        links = ''
        
        # no node visited so far, present the first node in the workflow 
        if len(results) == 0:
            inode = self.firstNode()
            style += inode.style(False)
            body += f'{inode.box()}\n'
            links += f'click {inode.id} onA\n'
        
        else:
            # iterate for all visited nodes
            for istep, iresult in enumerate(results):

                # when a step is defined, draw only until this step
                if step is not None:
                    if (istep+1)>step : 
                        break

                # this is the visited node, show it greyed out
                iid = iresult['id']
                inode = self.getNode(iid)
                style += inode.style(True)
                links += f'click {inode.id} onA\n'

                # show all nodes linked to visited nodes
                # for task, show next task (pending task)
                if inode.category == 'TASK':
                    next_nodes = self.nextNodeList(iid)
                    for jid in next_nodes:
                        visited = jid in node_path
                        ibody, istyle, ilinks = self.graphNext(jid, inode, None, visited)
                        body += ibody
                        style+= istyle
                        links+= ilinks

                # for decision, show decision taken in the visited node
                elif inode.category == 'LOGICAL':
                    idecision = iresult['decision']
                    if idecision == True:
                        next_nodes_true  = self.logicalNodeList(iid, True)
                        for jid in next_nodes_true:
                            visited = jid in node_path
                            ibody, istyle, ilinks = self.graphNext(jid, inode, True, visited)
                            body += ibody
                            style+= istyle
                            links+= ilinks

                    else:
                        next_nodes_false =self.logicalNodeList(iid, False)
                        for jid in next_nodes_false:
                            visited = jid in node_path
                            ibody, istyle, ilinks = self.graphNext(jid, inode, False, visited)
                            body += ibody
                            style+= istyle
                            links+= ilinks

        return (header+body+style+links)





   