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

import pickle
import numpy as np
import json

class NAM:
    def __init__(self, name, description=None):
        self.name = name
        self.decription = description

class substance:
    def __init__(self, name, ID, CASRN=None, SMILES=None):
        self.name = name
        self.ID = ID
        self.CASRN=CASRN
        self.SMILES=SMILES

class endpoint:
    def __init__(self, name, description=None):
        self.name = name
        self.decription = description

class ra:
    ''' Class storing all the risk assessment information
    '''
    def __init__(self):
        ''' constructor '''
        self.ID = {}
        self.results = {}
        self.NAMS = []
        self.substances = []
        self.endpoints = []
        self.error = None
        self.warning = None

    def load (self):
        print ('load')

    def save (self):
        print ('save')

    def getJSON (self):
        print ('getJSON')
        temp_json = {}
        temp_json['ID']=self.ID
        temp_json['results']=self.results
        temp_json['NAMS']=self.NAMS
        temp_json['substances']=self.substances
        temp_json['endpoints']=self.endpoints
        return json.dumps(temp_json, allow_nan=True)
