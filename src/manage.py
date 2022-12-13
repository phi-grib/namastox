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
import shutil
import pickle
from logger import get_logger
from utils import ra_tree_path 

LOG = get_logger(__name__)

def action_new(raname):
    '''
    Create a new ra tree, using the given name.
    This creates the development version "dev",
    copying inside default child classes
    '''

    if not raname:
        return False, 'empty raname label'

    # importlib does not allow using 'test' and issues a misterious error when we
    # try to use this name. This is a simple workaround to prevent creating ranames 
    # with this name 
    if raname == 'test':
        return False, 'the name "test" is disallowed, please use any other name'

    # raname directory with /dev (default) level
    ndir = ra_tree_path(raname)
    if os.path.isdir(ndir):
        return False, f'Endpoint {raname} already exists'
    try:
        os.mkdir(ndir)
        LOG.info(f'{ndir} created')
    except:
        return False, f'Unable to create path for {raname} endpoint'

    ndev = os.path.join (ndir, 'dev')
    try:
        os.mkdir(ndev)
        LOG.info(f'{ndev} created')
    except:
        return False, f'Unable to create path for {raname} endpoint'

    # Copy classes skeletons to ndir
    wkd = os.path.dirname(os.path.abspath(__file__))
    children_names = ['ra.yaml', 'documentation.yaml']

    for cname in children_names:
        src_path = os.path.join (wkd, cname)
        try:
            shutil.copy(src_path, ndev)
        except:
            return False, f'Unable to copy {cname} file'

    LOG.debug(f'copied class skeletons from {src_path} to {ndev}')

    LOG.info(f'New endpoint {raname} created')
    return True, 'new endpoint '+raname+' created'
