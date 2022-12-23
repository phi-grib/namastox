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
import yaml
import shutil
import pickle
from logger import get_logger
from utils import ra_tree_path, ra_repository_path
from ra import Ra

LOG = get_logger(__name__)

# TODO: this should be a class!!!



def action_update(raname, ifile, ofile=None):
    '''
        ***
    '''

    # instantiate a ra object
    ra = Ra()
    succes, results = ra.loadYaml(raname,0)
    if not succes:
        return False, results

    # read delta and use it to change existing delra
    if not os.path.isfile(ifile):
        return False, f'{ifile} not found'
    
    with open(ifile,'r') as inputf:
        delta_dict = yaml.safe_load(inputf)

    ra.applyDelta(delta_dict)

    # process ra using expert logic
    ra.appyExpert()

    # dump new version
    results = ra.dumpUpdate()

    if ofile is None:
        for iline in results:
            print (iline)
    else:
        with open(ofile,'w') as outputf:
            for iline in results:
                outputf.write (iline+'\n')
    
    # save new version and replace the previous one
    ra.save()

    return True, results