#!/usr/bin/env python3
#
# Copyright 2024 Hewlett Packard Enterprise Development LP.
#

import json
import os.path
import argparse
import traceback
from os import path
from manageresources import ManageResources
from jinja2 import Environment, FileSystemLoader

def logtodict(log):
    results = []
    for row in log.readlines():
        results.append(json.loads(row))
    return results

def main():
    benk = ManageResources(None)

    parser = argparse.ArgumentParser(
                prog='outputter.py',
                description='Reads a sequencer log and outputs in a specific template format',
                epilog='(c) Hewlett Packard Enterprise LP 2023')

    parser.add_argument('-l', '--log', type=argparse.FileType('r'), 
                        metavar='sequence-*.log', dest='slog', help='A single sequence log')
    parser.add_argument('-a', '--alog', type=argparse.FileType('r'), 
                        metavar='sequence-A-*.log', dest='alog', help='A sequence log of a A test')
    parser.add_argument('-b', '--blog', type=argparse.FileType('r'), 
                        metavar='sequence-B-*.log', dest='blog', help='A sequence log of a B test')
    parser.add_argument('-t', '--template', type=argparse.FileType('r'), 
                        metavar='mytemplate.j2', dest='jtpl', required=True, help='A jinja2 template')

    args = parser.parse_args()

    if args.slog and (args.alog or args.blog):
        print('error: single log specified with A/B log')
        parser.print_help()
        exit(1)

    if not args.slog and (not args.alog or not args.blog): 
        print('error: need a single log or A/B logs')
        parser.print_help()
        exit(1)
    
    try:
        path_elements = os.path.split(args.jtpl.name)

        environment = Environment(loader=FileSystemLoader(path_elements[0]))

        environment.trim_blocks=True
        environment.lstrip_blocks=True

        template = environment.get_template(path_elements[1])

        slog = []
        alog = []
        blog = []
        meta = {}

        if args.slog:
            slog = logtodict(args.slog)
            meta['log'] = args.slog.name
        if args.alog:
            alog = logtodict(args.alog)
            meta['alog'] = args.alog.name
        if args.blog:
            blog = logtodict(args.blog)
            meta['blog'] = args.blog.name

        print(template.render(log=slog, a=alog, b=blog, meta=meta), end='')

    except:
        print('error: unable to parse')
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()
