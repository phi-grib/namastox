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
        elif 'values' in iresult:
            oline = f'task   {iresult["id"]} val:{iresult["values"]} summary: {iresult["summary"]} '
        else:
            oline = ''

        LOG.info(oline)
        output.append(oline)

    # output for WEB
    if out=='json':
        odict = []
        for iresult in results:
            if 'decision' in iresult:
                odict.append({'id':iresult['id'],'name':iresult['name'],'summary':iresult['summary'],'decision':iresult['decision'] })
            elif 'values' in iresult:
                odict.append({'id':iresult['id'],'name':iresult['name'],'summary':iresult['summary'],'values':iresult['values'] })
        return True , odict
        
    return True, f'{len(output)} results found for {raname}'

def action_result(raname, resultid, out='text'):
    ''' returns the a given results this raname
    '''
    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load()
    if not succes:
        return False, results

    # get a dictionary with the ra.yaml contents that can
    # be passed to the GUI or shown in screen

    iresult = ra.getResult(resultid)
    if iresult is None:
        return False, 'result not found'
    
    if out=='json':
        return True, iresult
    
    if 'decision' in iresult:
        LOG.info({'id':iresult['id'],'summary':iresult['summary'],'decision':iresult['decision'] })
    elif 'values' in iresult:
        LOG.info({'id':iresult['id'],'summary':iresult['summary'],'values':iresult['values'] })
    
    return True, 'result found'
    
def action_task(raname, resultid):
    ''' returns the task resultid
    '''
    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load()
    if not succes:
        return False, results
    
    itask = ra.getTask(resultid)
    if itask is None:
        return False, 'result not found'
    
    return True, itask

def action_pendingTasks(raname):
    ''' returns a list of dictionaries with a short description of the pending tasks
    '''
    ra = Ra(raname)
    succes, results = ra.load()
    if not succes:
        return False, results
    
    active_nodes = ra.getActiveNodes()

    if len(active_nodes)>0:
        return True, active_nodes
    else:
        return False, 'no active nodes'

def action_pendingTask(raname, resultid):
    ''' returns a dictionary with a template of the pending task resultid
    '''
    ra = Ra(raname)
    succes, results = ra.load()
    if not succes:
        return False, results
    
    active_node = ra.getActiveNode(resultid)

    if active_node is not None:
        return True, active_node
    else:
        return False, f'active node {resultid} not found'

