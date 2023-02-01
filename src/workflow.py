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

import yaml
import os
import pandas as pd
from src.utils import ra_path
from src.node import Node
from src.logger import get_logger

LOG = get_logger(__name__)


class Workflow:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self, raname):
        ''' constructor '''
        self.nodes = []
        self.rapath = ra_path(raname)

        success = self.load()
        if not success:
            success = self.import_table()


    def import_table (self):
        table_path = os.path.join (self.rapath,'workflow.csv')
        table_dataframe = pd.read_csv(table_path, sep='\t')
        table_dict = table_dataframe.to_dict('list')
        print (table_dict)

        node_ids = table_dict['ID']
        node_names = table_dict['Name']
        node_types = table_dict['Type']
        for i in range(table_dataframe.shape[0]):
            node_task = {}
            self.nodes.append(Node(node_ids[i], node_names[i], node_types[i], node_task))

        # save pickl

        return True
         
    def load(self):       
        ''' load the Expert object from a pickle
        '''
        table_path = os.path.join (self.rapath,'workflow.pkl')
        if not os.path.isfile(table_path):
            return self.import_table()
        
        # with open(table_path,'rb') as f:


       
        return True

    def save (self):
        ''' saves the Expert object to a JSON file
        '''
        expname = os.path.join (self.rapath,'expert.yaml')
        with open(expname,'w') as f:
            f.write(yaml.dump({"rules":self.rules}))



   