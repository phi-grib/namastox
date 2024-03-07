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

        self.nodes = {}
        self.firstNodeId = ''
        self.rapath = ra_path(raname)

        # try to load a pickle created previously
        success = self.load()

        # if not found import from the file defined in self.workflow
        if not success:
            success = self.import_table()

        if not success:
            LOG.error('CRITICAL: unable to load a correct workflow definition')
            sys.exit(-1)

    def import_table (self):
        ''' parse a TSV defining the workflow '''

        table_path = os.path.join (self.rapath,self.workflow)
        
        LOG.info (f'import table {table_path}')

        table_dataframe = pd.read_csv(table_path, sep='\t').replace(np.nan, None)
        table_dict = table_dataframe.to_dict('list')

        # minimum elements in the TSV
        index_labels = ['id', 'label', 'name', 'category', 'next_node', 'next_yes', 'next_no']
        for i in index_labels:
            if not i in table_dict:
                return False

        # for every table row...
        for i in range(table_dataframe.shape[0]):

            # create a new node, by creating an empty dictionary
            # and copying everying inside
            node_content = {}
            for key in table_dict:
                value = table_dict[key][i] 
                node_content[key]=value   

            # append the node to the list of nodes
            self.nodes[node_content['id']] = Node(node_content)
             
            if i==0:
                self.firstNodeId = node_content['id']

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
            self.firstNodeId = pickle.load(f)
            
        return True

    def save (self):
        ''' saves the Expert object to a pickl
        '''
        pickl_path = os.path.join (self.rapath,'workflow.pkl')
        with open(pickl_path,'wb') as f:
            pickle.dump(self.nodes, f, protocol=pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.firstNodeId, f, protocol=pickle.HIGHEST_PROTOCOL)

    def getNode (self, iid):
        if iid in self.nodes:
            return self.nodes[iid]
        return None

    def getTask (self, iid):
        if iid in self.nodes:
            return self.nodes[iid].getTask()    
        return None    
            
    def firstNode (self):
        return self.nodes[self.firstNodeId]
    
    def nextNodeList (self, id):
        return self.nodes[id].nextNodes()
    
    def logicalNodeList (self, id, decision):
        return self.nodes[id].nextLogicalNodes(decision)
    
    def graphNext (self, nodeid, inode, decision=None, visited=False):
        inext = self.getNode(nodeid)
        arrow = '-->'
        if decision is True:
            arrow = '--Y-->'
        elif decision is False:
            arrow = '--N-->'
        ibody = f'{inode.box()}{arrow}{inext.box()}\n'
        istyle = inext.style(visited=visited, future=False)
        ilinks = f'click {inext.id} onA\n'

        if inext.category == 'LOGICAL' and not visited:
            next_nodes_true  =self.logicalNodeList(nodeid, True)
            for jid in next_nodes_true:
                ilog = self.getNode(jid)
                ibody += f'{inext.box()}--Y-->{ilog.box()}\n'
                istyle += ilog.style(True, True)
                ilinks += f'click {ilog.id} onA\n'

            next_nodes_false  =self.logicalNodeList(nodeid, False)
            for jid in next_nodes_false:
                ilog = self.getNode(jid)
                ibody += f'{inext.box()}--N-->{ilog.box()}\n'
                istyle += ilog.style(True, True)
                ilinks += f'click {ilog.id} onA\n' 
             
        return ibody, istyle, ilinks
        
    def getTaskName (self, id):
        if id in self.nodes:
            itask = self.nodes[id].getTask()
            return itask.getName()
        
        return None

    def recurse (self, id):
        for inode in self.nodes:
            next_list = self.nodes[inode].nextNodes()
            if id in next_list:
                self.recurse_list.append(inode)
                self.recurse(inode)
        
    def getUpstreamNodes (self, id):
        if not id in self.nodes:
            return []                
        self.recurse_list = []
        self.recurse(id)
        return (self.recurse_list)

    def isVisitedNode(self, id, results):
        node_path =[iresult['id'] for iresult in results]

        if id in node_path:
            return True
        
        return False

    def getWorkflowGraph (self, results, step=None):

        node_path =[iresult['id'] for iresult in results]

        header = 'graph TD\n'
        body = ''
        style = ''
        links = ''
        
        # no node visited so far, present the first node in the workflow 
        if len(results) == 0:
            inode = self.firstNode()
            style += inode.style(False, False)
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
                style += inode.style(True, False)
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





   