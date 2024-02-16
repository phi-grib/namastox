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
import os

LOG = get_logger(__name__)

def action_notes(raname, step=None, out='json'):
    ''' returns the list of results available for this raname/step
    '''

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load(step)

    if not succes:
        return False, results

    notes = ra.getNotes()

    return True, notes

def action_note(raname, noteid):
    ''' returns a given note for this raname
    '''

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load()
    
    if not succes:
        return False, results

    notes = ra.getNotes()

    for inote in notes:
        if 'id'in inote and inote['id'] == noteid:
            return True, inote

    return False, f'no note with id {noteid} found'

def action_note_add (raname, note):
    ''' adds the note given as argument to this raname
    '''

    # instantiate a ra object
    ra = Ra(raname)
    succes, results = ra.load()

    if not succes:
        return False, results

    # use input dictionary to update RA
    success = ra.addNote(note)

    if not success:
        return False, 'note not added'
    
    # save new version and replace the previous one
    ra.save()
    
    return True, 'OK'
