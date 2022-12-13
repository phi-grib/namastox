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

import argparse
import yaml
import os
from logger import get_logger
from config import configure
from manage import action_new, action_kill, action_list, action_publish

LOG = get_logger(__name__)

def main():

    LOG.debug('-------------NEW RUN-------------\n')

# TODO
# create template ra.yaml
# output empty template on new
# implement update:
#  - parse input to create new ra object
#  - process ra using expert logic
#  - output new ra object


# -n --new -e NAME -o template.yaml
# -u --update -e NAME -i template.yaml 
# -r --report -e NAME -o template.yaml -p result.pdf

    parser = argparse.ArgumentParser(description='NAMASTOX')

    parser.add_argument('-c', '--command',
                        action='store',
                        choices=['config', 'new', 'kill', 'list', 'publish', 'update', 'report'],
                        help='Action type: \'config\' or \'new\' or \'kill\' or \'list\' or \'publish\''
                        '\'update\' or \'report\'',
                        required=True)

    parser.add_argument('-r', '--raname',
                        help='Name of RA',
                        required=False)

    parser.add_argument('-i', '--infile',
                        help='input YAML file',
                        required=False)
    
    parser.add_argument('-o', '--outfile',
                        help='output YAML file',
                        required=False)

    parser.add_argument('-p', '--pdf',
                        help='report in PDF format',
                        required=False)
    
    parser.add_argument('-d', '--directory',
                        help='configuration dir',
                        required=False)
    
    parser.add_argument('-a', '--action',
                        help='action',
                        required=False)

    args = parser.parse_args()

    if args.infile is not None:
        if not os.path.isfile(args.infile):
            LOG.error(f'Input file {args.infile} not found')
            return 

    # make sure flame has been configured before running any command, unless this command if used to 
    # configure flame
    # if args.command != 'config':
    #     utils.config_test()

    if args.command == 'config':
        success, results = configure(args.directory, (args.action == 'silent'))
        if not success:
            LOG.error(f'{results}, configuration unchanged')

    elif args.command == 'new':
        if (args.raname is None):
            LOG.error('namastox new : raname argument is compulsory')
            return
        success, result = action_new(args.raname)

    elif args.command == 'list':
        success, result = action_list(args.raname)   

    elif args.command == 'kill':
        if (args.raname is None):
            LOG.error('namastox kill : raname argument is compulsory')
            return
        success, result = action_kill(args.raname)   

    elif args.command == 'publish':
        if (args.raname is None):
            LOG.error('namastox publish : raname argument is compulsory')
            return
        success, result = action_publish(args.raname)  

    elif args.command == 'update':
        if (args.raname is None):
            LOG.error('flame predict : raname and input file arguments are compulsory')
            return

        LOG.info ('UPDATE >>>>>>>>')

    elif args.command == 'report':
        if (args.raname is None):
            LOG.error('flame predict : raname and input file arguments are compulsory')
            return

        LOG.info ('REPORT >>>>>>>>>')

if __name__ == '__main__':
    main()
