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

def action_notes(raname, step=None, out='text'):
    ''' returns the list of results available for this raname/step
    '''

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load(step)
    if not succes:
        return False, results

    # get a dictionary with the ra.yaml contents that can
    # be passed to the GUI or shown in screen
    notes = ra.getNotes()

    LOG.debug(f'Retrieved notes for {raname}')
    
    output = []
    for inote in notes:
        if 'id' not in inote or 'author' not in inote or 'date' not in inote:
            continue
        oline = f'{inote["id"]} author:{inote["author"]} date: {inote["date"]} '
        
        LOG.info(oline)
        output.append(oline)

    if out=='json':
        return True, output
    
    return True, f'{len(output)} notes found for {raname}'

def action_note(raname, noteid, out='text'):
    ''' returns a given note for this raname
    '''

    return True, f"get note {noteid} for {raname}. Not implemented"