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
from namastox.ra import Ra

LOG = get_logger(__name__)

def action_status(raname, step=None, ofile=None, out='text'):
    ''' return status of RA "raname", at step "step"
    '''

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load(step)
    if not succes:
        return False, results

    # get a dictionary with the ra.yaml contents that can
    # be passed to the GUI or shown in screen
    status = ra.getStatus()

    LOG.debug(f'Retrieved status for {raname}')
    
    # info = ra.getGeneralInfo()

    for ikey in status:
        ielement = status[ikey]
        for jkey in ielement:
            jelement = ielement[jkey]
            LOG.info(f'{ikey} : {jkey} : {jelement}')

    # for ikey in info:
    #     ielement = info[ikey]
    #     for jkey in ielement:
    #         jelement = ielement[jkey]
    #         LOG.info(f'{ikey} : {jkey} : {jelement}')

    if ofile is not None:
        # get a template to get required data
        template = ra.getTemplate()

        # write template for next update
        with open(ofile,'w') as outputf:
            outputf.write (template)    

    if out=='json':
        return True, status
    
    return True, f'completed status for {raname}'