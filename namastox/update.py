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
from namastox.logger import get_logger
from namastox.ra import Ra

LOG = get_logger(__name__)

def action_update(raname, ifile, ofile=None):
    ''' use the input file to update RA. The new version is submitted to the expert to 
        further change RA. The final version of RA is stored in the repository and copied
        in the historic archive 
    '''

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load()
    if not succes:
        return False, results

    # read input file
    if not os.path.isfile(ifile):
        return False, f'{ifile} not found'
    
    # convert to a dictionary 
    with open(ifile,'r') as inputf:
        input_dict = yaml.safe_load(inputf)

    # use input dictionary to update RA
    success, results = ra.update(input_dict)

    if not success:
        return False, 'update not completed'
    
    # save new version and replace the previous one
    ra.save()

    # dump a template to get required data
    results = ra.getTemplate()

    # write template for next update
    with open(ofile,'w') as outputf:
        outputf.write (results)    

    return True, f'{raname} updated'