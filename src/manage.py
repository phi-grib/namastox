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
from utils import ra_tree_path, ra_repository_path, ra_path

LOG = get_logger(__name__)

def action_new(raname, outfile=None):
    '''
    Create a new risk assessment tree, using the given name.
    This creates the development version "dev",
    copying inside default child classes
    '''

    if not raname:
        return False, 'empty risk assessment name'

    # importlib does not allow using 'test' and issues a misterious error when we
    # try to use this name. This is a simple workaround to prevent creating ranames 
    # with this name 
    if raname == 'test':
        return False, 'the name "test" is disallowed, please use any other name'

    # raname directory with /dev (default) level
    ndir = ra_tree_path(raname)
    if os.path.isdir(ndir):
        return False, f'Risk assessment {raname} already exists'
    try:
        os.mkdir(ndir)
        LOG.debug(f'{ndir} created')
    except:
        return False, f'Unable to create path for {raname} endpoint'

    ndev = os.path.join (ndir, 'dev')
    try:
        os.mkdir(ndev)
        LOG.debug(f'{ndev} created')
    except:
        return False, f'Unable to create path for {raname} endpoint'

    # Copy templates
    wkd = os.path.dirname(os.path.abspath(__file__))
    template_names = ['ra.yaml', 'expert.yaml']

    for cname in template_names:
        src_path = os.path.join (wkd, cname)
        try:
            shutil.copy(src_path, ndev)
        except:
            return False, f'Unable to copy {cname} file'

    LOG.debug(f'copied risk assessment templates from {src_path} to {ndev}')

    # Instantiate Ra
    ra = Ra()
    success, results = ra.load(raname, 0)
    if not success:
        return False, results

    # Include RA information 
    ra.setVal('raname',raname)
    ra.setVal('version',0)
    ra.setVal('rapath',ra_path(raname, 0))
    ra.setHash()

    # Save
    ra.save()

    # Show template
    yaml = ra.dumpYAML(['substances', 'endpoints'])
    
    if outfile is None:
        for iline in yaml:
            print (iline)
    else:
        with open(outfile,'w') as f:
            for iline in yaml:
                f.write (iline+'\n')

    return True, f'New risk assessment {raname} created'

def action_kill(raname):
    '''
    removes the ra tree described by the argument
    '''

    if not raname:
        return False, 'Empty risk assessment name'

    ndir = ra_tree_path(raname)

    if not os.path.isdir(ndir):
        return False, f'Risk assessment {raname} not found'

    try:
        shutil.rmtree(ndir, ignore_errors=True)
    except:
        return False, f'Failed to remove risk assessment {raname}'

    return True, f'Risk assessment {raname} removed'

def action_list(raname):
    '''
    In no argument is provided lists all ranames present at the repository 
     otherwyse lists all versions for the raname provided as argument
    '''

    # if no raname name is provided, just list the raname names
    if not raname:
        rdir = ra_repository_path()
        if os.path.isdir(rdir) is False:
            return False, 'The risk assessment name repository path does not exist. Please run "namastox -c config".'

        num_ranames = 0
        LOG.info('Risk assessment(s) found in repository:')
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
        LOG.debug(f'Retrieved list of risk assessments from {rdir}')
        return True, f'{num_ranames} risk assessment(s) found'
        # if a raname name is provided, list versions

    base_path = ra_tree_path(raname)

    num_versions = 0
    for x in os.listdir(base_path):
        if x.startswith("ver"):
            num_versions += 1
            LOG.info(f'\t{raname} : {x}')

    return True, f'Risk assessment {raname} has {num_versions} published versions'

def action_publish(raname):
    '''
    clone the development "dev" version as a new raname version,
     assigning a sequential version number
    '''

    if not raname:
        return False, 'Empty risk assessment name'

    base_path = ra_tree_path(raname)

    if not os.path.isdir(base_path):
        #LOG.error(f'raname {raname} not found')
        return False, f'Risk assessment {raname} not found'

    # gets version number
    v = [int(x[-6:]) for x in os.listdir(base_path) if x.startswith("ver")]

    if not v:
        max_version = 0
    else:
        max_version = max(v)

    new_path = os.path.join(base_path,f'ver{max_version+1:06}')

    if os.path.isdir(new_path):
        #LOG.error(f'Versin {v} of raname {raname} not found')
        return False, f'Version {max_version+1} of risk assessment {raname} already exists'

    src_path = os.path.join (base_path,'dev')

    try:
        shutil.copytree(src_path, new_path)
    except:
        return False, f'Unable to copy contents of dev version for risk assessment {raname}'

    return True, f'New risk assessment version created from {src_path} to {new_path}'


