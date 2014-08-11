#!/usr/bin/env python
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import print_function

from argparse import ArgumentParser

from tuskar.storage.load_templates import load_templates


def parse_args(args=None):

    parser = ArgumentParser(description="")

    parser.add_argument(
        'directory',
        help="The directory to import templates from."
    )

    parser.add_argument(
        '--dry-run',
        help=("Find the templates and print them out without commiting them "
              "to the store."),
        action='store_true'
    )

    return parser.parse_args(args)


def _print_names(message, names):
    print("{0}: \n    {1}".format(message, '\n    '.join(names)))


def main(args=None):

    args = parse_args(args=args)

    all_templates, created, updated = load_templates(args.directory,
                                                     args.dry_run)

    if len(created):
        _print_names("Created", created)

    if len(updated):
        _print_names("Updated", updated)

    if not args.dry_run:
        print("Imported {0} templates".format(len(all_templates)))
    else:
        _print_names("Found", all_templates)
        print("Imported 0 templates")
