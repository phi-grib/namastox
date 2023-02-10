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

def action_results(raname, step=None, out='text'):
    ''' returns the list of results available for this raname/step
    '''

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load(step)
    if not succes:
        return False, results

    # get a dictionary with the ra.yaml contents that can
    # be passed to the GUI or shown in screen
    results = ra.getResults()

    LOG.debug(f'Retrieved results for {raname}')
    
    # screen output
    output = []
    for iresult in results:
        if 'decision' in iresult:
            oline = f'decision {iresult["id"]} dec:{iresult["decision"]} summary: {iresult["summary"]} '
        elif 'value' in iresult:
            oline = f'task   {iresult["id"]} val:{iresult["value"]} summary: {iresult["summary"]} '
        else:
            oline = ''

        LOG.info(oline)
        output.append(oline)

    # output for WEB
    if out=='json':
        odict = []
        for iresult in results:
            if 'decision' in iresult:
                odict.append({'id':iresult['id'],'summary':iresult['summary'],'decision':iresult['decision'] })
            elif 'value' in iresult:
                odict.append({'id':iresult['id'],'summary':iresult['summary'],'decision':iresult['value'] })
        return True , odict
        
    return True, f'{len(output)} results found for {raname}'

def action_result(raname, resultid, out='text'):
    ''' returns the a given results this raname
    '''

    return True, f"get result {resultid} for {raname}. Not implemented"