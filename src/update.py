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

import os
import shutil
import pickle
from logger import get_logger
from utils import ra_tree_path, ra_repository_path
import ra

LOG = get_logger(__name__)

# TODO: this should be a class!!!

def action_update(raname, ifile, ofile):
    '''
        ***
    '''
    ira = ra.ra( )
    succes, results = ira.loadYaml(raname, 0)
    print (ira.getJSON())

    # parse input to create new ra object


    # process ra using expert logic

    # output new ra object
