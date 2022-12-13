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

LOG = get_logger(__name__)

def main():

    LOG.debug('-------------NEW RUN-------------\n')

# -c --config
# -n --new -e NAME -o template.yaml
# -u --update -e NAME -i template.yaml 
# -r --report -e NAME -o template.yaml -p result.pdf

    parser = argparse.ArgumentParser(description='NAMASTOX')

    parser.add_argument('-c', '--command',
                        action='store',
                        choices=['config', 'new', 'update', 'report'],
                        help='Action type: \'config\' or \'new\' or \'update\' or \'report\'',
                        required=True)

    parser.add_argument('-e', '--endpoint',
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

    if args.command == 'new':

        if (args.endpoint is None):
            LOG.error('flame predict : endpoint and input file arguments are compulsory')
            return

        LOG.info ('NEW')

    elif args.command == 'update':
        
        if (args.endpoint is None):
            LOG.error('flame predict : endpoint and input file arguments are compulsory')
            return

        LOG.info ('UPDATE')

    elif args.command == 'report':
        
        if (args.endpoint is None):
            LOG.error('flame predict : endpoint and input file arguments are compulsory')
            return

        LOG.info ('REPORT')

        

if __name__ == '__main__':
    main()
