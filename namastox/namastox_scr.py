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
import argparse
from namastox.logger import get_logger
from namastox import __version__
from namastox.config import configure
from namastox.manage import action_new, action_kill, action_list, action_steps, action_info
from namastox.update import action_update
from namastox.status import action_status
from namastox.report import action_report

LOG = get_logger(__name__)

def main():

    LOG.debug('-------------NEW RUN-------------\n')

    results = None
    parser = argparse.ArgumentParser(description='NAMASTOX')

    parser.add_argument('-c', '--command',
                        action='store',
                        choices=['config', 'new', 'kill', 'list', 'steps', 'info',  'status', 'update', 'report'],
                        help='Action type: \'config\' or \'new\' or \'kill\' or \'list\' or \'steps\' or \'info\' '
                        'or \'status\' or \'update\' or \'report\'',
                        required=True)

    parser.add_argument('-r', '--raname',
                        help='Name of RA',
                        required=False)

    parser.add_argument('-s', '--step',
                        help='RA workflow step',
                        required=False)
    
    parser.add_argument('-v', '--version',
                        help='RA version',
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

    parser.add_argument('-w', '--word',
                        help='report in Word format',
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
        if (args.raname is None or args.outfile is None ):
            LOG.error('namastox new : raname and output file arguments are compulsory')
            return
        success, results = action_new(args.raname, args.outfile)

    elif args.command == 'list':
        success, results = action_list()   

    elif args.command == 'steps':
        if (args.raname is None ):
            LOG.error('namastox steps : raname argument is compulsory')
            return
        success, results = action_steps(args.raname)   

    elif args.command == 'info':
        if (args.raname is None ):
            LOG.error('namastox info : raname argument is compulsory')
            return
        success, results = action_info(args.raname)   

    elif args.command == 'kill':
        if (args.raname is None):
            LOG.error('namastox kill : raname argument is compulsory')
            return
        success, results = action_kill(args.raname)   

    elif args.command == 'status':
        if (args.raname is None):
            LOG.error('namastox status : raname argument is compulsory')
            return
        success, results = action_status(args.raname, args.step, args.outfile)   

    elif args.command == 'update':
        if (args.raname is None or args.infile is None or args.outfile is None ):
            LOG.error('namastox update : raname, input file and output file arguments are compulsory')
            return
        success, results = action_update (args.raname, args.infile, args.outfile)

    elif args.command == 'report':
        if (args.raname is None or (args.pdf is None and args.word is None)):
            LOG.error('namastox report : raname and PDF or Word output file arguments are compulsory')
            return

        success, results = action_report (args.raname, args.pdf, args.word)
    
    if results is not None and type(results) != dict:
        LOG.info (results)

if __name__ == '__main__':
    main()