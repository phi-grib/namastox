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
from ra import Ra
from utils import ra_tree_path, ra_repository_path

LOG = get_logger(__name__)

def action_new(raname, outfile=None):
    '''
    Create a new ra tree, using the given name.
    This creates the development version "dev",
    copying inside default child classes
    '''

    if not raname:
        return False, 'empty ra name'

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

    # Copy templates
    wkd = os.path.dirname(os.path.abspath(__file__))
    template_names = ['ra.yaml', 'documentation.yaml', 'expert.json']

    for cname in template_names:
        src_path = os.path.join (wkd, cname)
        try:
            shutil.copy(src_path, ndev)
        except:
            return False, f'Unable to copy {cname} file'

    LOG.debug(f'copied ra templates from {src_path} to {ndev}')

    ra = Ra()
    ra.loadYaml(raname, 0)
    yaml = ra.dumpYAML()
    if outfile is None:
        for iline in yaml:
            print (iline)
    else:
        with open(outfile) as f:
            f.write(yaml) 

    # Dump yaml


    LOG.info(f'New ra {raname} created')
    return True, 'new ra '+raname+' created'


def action_kill(raname):
    '''
    removes the ra tree described by the argument
    '''

    if not raname:
        return False, 'Empty ra name'

    ndir = ra_tree_path(raname)

    if not os.path.isdir(ndir):
        return False, f'Ra {raname} not found'

    try:
        shutil.rmtree(ndir, ignore_errors=True)
    except:
        return False, f'Failed to remove ra {raname}'

    LOG.info(f'ra {raname} removed')
    #print(f'raname {raname} removed')
    return True, f'ra {raname} removed'


def action_list(raname):
    '''
    In no argument is provided lists all ranames present at the repository 
     otherwyse lists all versions for the raname provided as argument
    '''

    # if no raname name is provided, just list the raname names
    if not raname:
        rdir = ra_repository_path()
        if os.path.isdir(rdir) is False:
            return False, 'the ranames repository path does not exist. Please run "flame -c config".'

        num_ranames = 0
        LOG.info('ra found in repository:')
        for x in os.listdir(rdir):
            xpath = os.path.join(rdir,x) 
            # discard if the item is not a directory
            if not os.path.isdir(xpath):
                continue
            # discard if the directory does not contain a 'dev' directory inside
            if not os.path.isdir(os.path.join(xpath,'dev')):
                continue
            num_ranames += 1
            LOG.info('\t'+x)
        LOG.debug(f'Retrieved list of ranames from {rdir}')
        return True, f'{num_ranames} ranames found'
        # if a raname name is provided, list versions

    base_path = ra_tree_path(raname)

    num_versions = 0
    for x in os.listdir(base_path):
        if x.startswith("ver"):
            num_versions += 1
            LOG.info(f'\t{raname} : {x}')

    return True, f'raname {raname} has {num_versions} published versions'

def action_publish(raname):
    '''
    clone the development "dev" version as a new raname version,
     assigning a sequential version number
    '''

    if not raname:
        return False, 'Empty ra name'

    base_path = ra_tree_path(raname)

    if not os.path.isdir(base_path):
        #LOG.error(f'raname {raname} not found')
        return False, f'raname {raname} not found'

    # gets version number
    v = [int(x[-6:]) for x in os.listdir(base_path) if x.startswith("ver")]

    if not v:
        max_version = 0
    else:
        max_version = max(v)

    new_path = os.path.join(base_path,f'ver{max_version+1:06}')

    if os.path.isdir(new_path):
        #LOG.error(f'Versin {v} of raname {raname} not found')
        return False, f'Version {max_version+1} of ra {raname} already exists'

    src_path = os.path.join (base_path,'dev')

    try:
        shutil.copytree(src_path, new_path)
    except:
        return False, f'Unable to copy contents of dev version for ra {raname}'

    LOG.info(f'New ra version created from {src_path} to {new_path}')
    return True, f'New ra version created from {src_path} to {new_path}'


