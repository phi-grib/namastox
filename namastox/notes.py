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

from namastox.ra import Ra
import os
import random
import string
from datetime import date

def action_notes(raname, user_name, step=None, out='json'):
    ''' returns the list of results available for this raname/step
    '''

    # instantiate a ra object
    ra = Ra(raname, user_name)
    succes, results = ra.load(step)

    if not succes:
        return False, results

    notes = ra.getNotes()

    return True, notes

def action_note(raname, user_name, noteid):
    ''' returns a given note for this raname
    '''

    # instantiate a ra object
    ra = Ra(raname, user_name)
    succes, results = ra.load()
    
    if not succes:
        return False, results

    notes = ra.getNotes()

    for inote in notes:
        if 'id'in inote and inote['id'] == noteid:
            return True, inote

    return False, f'no note with id {noteid} found'


def action_note_add (raname, user_name,  note):
    ''' adds the note given as argument to this raname
    '''

    # instantiate a ra object
    ra = Ra(raname, user_name)
    succes, results = ra.load()

    if not succes:
        return False, results

    # generate a random ID
    note['id'] =  ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
    
    # add current date
    today = date.today()
    note['date'] = today.strftime("%d/%m/%Y")

    # use input dictionary to update RA
    success = ra.addNote(note)

    if not success:
        return False, 'note not added'
    
    # save new version 
    ra.save()
    
    return True, 'OK'


def action_note_delete(raname, user_name, noteid):
    ''' remove a given note for this raname
    '''

    # instantiate a ra object
    ra = Ra(raname, user_name)
    succes, results = ra.load()
    
    if not succes:
        return False, results

    notes = ra.getNotes()

    for inote in notes:
        if 'id'in inote and inote['id'] == noteid:
            notes.remove(inote)
            # save new version 
            ra.save()
            return True, 'OK'


    return False, f'no note with id {noteid} found'
