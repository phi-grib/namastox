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
from src.logger import get_logger
from src.ra import Ra
from src.expert import Expert

LOG = get_logger(__name__)

def action_update(raname, ifile, ofile=None):
    ''' use the input file to update RA. The new version is submitted to the expert to 
        further change RA. The final version of RA is stored in the repository and copied
        in the historic archive 
    '''

    # instantiate a ra object
    ra = Ra()
    succes, results = ra.load(raname)
    if not succes:
        return False, results

    # read delta and use it to change existing delra
    if not os.path.isfile(ifile):
        return False, f'{ifile} not found'
    
    with open(ifile,'r') as inputf:
        delta_dict = yaml.safe_load(inputf)

    ra.applyDelta(delta_dict)

    # process ra using expert logic
    expert = Expert (raname)
    success, result = expert.load()
    if not success:
        return False, result

    success, result = expert.applyExpert(ra)
    if not success:
        return False, result

    # dump new version
    results = ra.dumpYAML()

    if ofile is None:
        for iline in results:
            LOG.info (iline)
    else:
        with open(ofile,'w') as outputf:
            for iline in results:
                outputf.write (iline+'\n')
    
    # save new version and replace the previous one
    ra.save()

    return True, f'{raname} updated'