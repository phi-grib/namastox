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
from src.logger import get_logger
from src.ra import Ra
from src.utils import ra_repository_path, ra_path, id_generator

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
    ndir = ra_path(raname)
    if os.path.isdir(ndir):
        return False, f'Risk assessment {raname} already exists'
    try:
        os.mkdir(ndir)
        os.mkdir(os.path.join(ndir,'hist'))
        os.mkdir(os.path.join(ndir,'repo'))
        LOG.debug(f'{ndir}, {ndir}/hist and {ndir}/repo created')
    except:
        return False, f'Unable to create path for {raname} endpoint'

    # Copy templates
    wkd = os.path.dirname(os.path.abspath(__file__))
    template_names = ['ra.yaml', 'workflow.csv']

    for cname in template_names:
        src_path = os.path.join (wkd, 'default', cname)
        try:
            shutil.copy(src_path, ndir)
        except:
            return False, f'Unable to copy {cname} file'

    LOG.debug(f'copied risk assessment templates from {src_path} to {ndir}')

    # Instantiate Ra
    ra = Ra(raname)
    success, results = ra.load()
    if not success:
        return False, results

    # Include RA information 
    ra.setVal('ID', id_generator() )

    # Save
    ra.save()

    # Show template
    yaml = ra.dumpYAML()
    
    if outfile is None:
        for iline in yaml:
            LOG.info(iline)
    else:
        with open(outfile,'w') as f:
            f.write(yaml)
            # for iline in yaml:
                # f.write (iline+'\n')

    return True, f'New risk assessment {raname} created'

def action_kill(raname):
    '''
    removes the ra tree described by the argument
    '''

    if not raname:
        return False, 'Empty risk assessment name'

    ndir = ra_path(raname)

    if not os.path.isdir(ndir):
        return False, f'Risk assessment {raname} not found'

    try:
        shutil.rmtree(ndir, ignore_errors=True)
    except:
        return False, f'Failed to remove risk assessment {raname}'

    return True, f'Risk assessment {raname} removed'

def action_list():
    '''
    In no argument is provided lists all ranames present at the repository 
     otherwyse lists all versions for the raname provided as argument
    '''

    # if no raname name is provided, just list the raname names
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

        num_ranames += 1
        LOG.info('\t'+x)

    LOG.debug(f'Retrieved list of risk assessments from {rdir}')
    return True, f'{num_ranames} risk assessment(s) found'
