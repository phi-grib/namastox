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

from src.logger import get_logger
from src.ra import Ra

LOG = get_logger(__name__)

def action_report(raname, pfile=None):
    ''' generate a report with the current status of the RA 
    '''

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load()
    if not succes:
        return False, results

    # show exec summary
    LOG.info (f'Risk assessment {raname}, ID {ra.getVal("ID")}')

    substances = ra.getVal("substances")
    if type(substances) == list:
        for isubs in substances:
            for key in isubs:
                LOG.info (f'substance {isubs[key]}') 

    endpoint = ra.getVal("endpoint")
    if type(endpoint) == dict:
        for iend in endpoint:
            LOG.info (f'endpoint {endpoint[iend]}') 

    LOG.info (f'Administration route {ra.getVal("administration_route")}')



    return True, results