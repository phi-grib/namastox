#! -*- coding: utf-8 -*-

# Description    Context wrapps calls to predict and build to
# support models making use of extenal input sources
#
# Authors:       Manuel Pastor (manuel.pastor@upf.edu)
#
# Copyright 2018 Manuel Pastor
#
# This file is part of NAMASTOX
#
# NAMASTOX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.
#
# NAMASTOX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NAMASTOX. If not, see <http://www.gnu.org/licenses/>.

import appdirs
import os
from namastox.utils import read_config, set_repositories

def configure(path: None, silent: False):
    """Configures model repository.

    Loads config.yaml and writes a correct model repository path
    with the path provided by the user or a default from appdirs
    if the path is not provided.
    """
    
    success, config = read_config()
    source_dir = ''
    if not success:
        return False, config

    ########################################################
    ###  Silent
    ########################################################

    if silent:
        if path is not None:  
            source_dir = os.path.abspath(path)
        else:
            source_dir = os.path.dirname(os.path.dirname(__file__)) 

        success = set_repositories(source_dir)
        
        if success:
            return True, config
        else:
            return False, 'error setting the repositories'

    ########################################################
    ###  Path not provided
    ########################################################
    if path is None:  # set default

        # If NAMASTOX has been already configured, just show values in screen and return values
        if config['config_status'] == True:
            for i in ['ras']:
                print (f'{i}: {config[i]}')
            return True, config

        # Assign defaults
        source_dir = appdirs.user_data_dir('namastox',False)
        if not os.path.isdir(source_dir):
            try:
                os.mkdir(source_dir)
            except Exception as e:
                return False, f'Error {e}'

    ########################################################
    ###  Path provided
    ########################################################
    else :
        try:
            source_dir = os.path.realpath(path)
        except:
            return False, f'input path {path} is not recognized as a valid path'

    ########################################################
    ###  Common
    ########################################################

    # if ask_user():
    success = set_repositories(source_dir)
    if success:
        return True, config
    else:
        return False, 'error setting the repositories'

