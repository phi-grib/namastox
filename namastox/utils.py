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
import yaml
import string
import random 

# def path_expand (path, version):
#     ''' 
#     Expands the path as required for the version provided as argument 
#     '''
#     if version == 0:
#         return os.path.join(path, 'dev')
#     else:
#         return os.path.join(path, 'ver%0.6d' % (version))

def ra_repository_path():
    '''
    Returns the path to the root of the raname repository,
    containing all ranames and versions
    '''
    success, config = read_config()
    if success: 
        return config['ras']

def ra_path(raname, user_name=''):
    '''
    Returns the path to the raname given as argumen, containg all versions
    '''
    if user_name == '':
        return os.path.join(ra_repository_path(), raname)
    else:
        return os.path.join(ra_repository_path(), user_name, raname)


# def ra_path(raname, version):
#     '''
#     Returns the path to the raname and version given as arguments
#     '''
#     return path_expand (ra_tree_path(raname), version)

def read_config():
    '''
    Reads configuration file "config.yaml" and checks
    sanity of raname repository path.

    Returns:
    --------
    Boolean, dict
    '''

    if 'namastox_configuration' in globals():
        return True, globals()['namastox_configuration']

    try:
        source_dir = os.path.dirname(os.path.dirname(__file__)) 
        config_nam = os.path.join(source_dir,'config.yaml')
        with open(config_nam,'r') as f:
            conf = yaml.safe_load(f)
    except Exception as e:
        return False, e

    if conf is None:
        return False, 'unable to obtain configuration file'

    # legacy configuration files contain individual items in the yaml
    if not 'root_repository' in conf:
        if 'ra_repository_path' in conf:
            base_dir, head_dir = os.path.split(conf['ra_repository_path'])
            conf['root_repository'] = base_dir
        else:
            return False, f'Configuration file incorrect. Run "namastox -c config -d ROOT_DIR" with a suitable ROOT_DIR setting'

    items = ['ras']
    for i in items:
        conf[i] = os.path.join(conf['root_repository'],i)

    if conf['config_status']:
        for i in items:
            try:
                conf[i] = os.path.abspath(conf[i])
            except:
                return False, f'Configuration file incorrect. Unable to convert "{conf[i]}" to a valid path.'
        
    globals()['namastox_configuration'] = conf

    return True, conf

def set_repositories(root_path):
    """
    Set the raname repository path.
    This is the dir where flame is going to create and load ranames.
    Returns:
    --------
    None
    """
    success, configuration = read_config()
    
    if not success:
        return False

    configuration['root_repository'] = root_path

    items = ['ras']
    for i in items:
        ipath = os.path.join(root_path, i)
        try:
            if not os.path.isdir(ipath):
                os.mkdir(ipath)
                print (f'...creating {ipath} directory')
            print (f'{i}: {ipath}')
        except Exception as e:
            print (f'Error {e}')
            return False

        configuration[i] = ipath

    write_config(configuration)

    return True

def write_config(config: dict) -> None:
    """Writes the configuration to disk"""
    config['config_status'] = True
    
    globals()['flame_configuration'] = config

    source_dir = os.path.dirname(os.path.dirname(__file__)) 
    with open(os.path.join(source_dir,'config.yaml'), 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    '''
    Return a random ID (used for temp files) with uppercase letters and numbers
    '''
    return ''.join(random.choice(chars) for _ in range(size))