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

from tuskar.storage.template_import import importer


def main():

    parser = ArgumentParser(description="")

    parser.add_argument(
        'directory',
        help="The directory to import templates from."
    )

    parser.add_argument(
        '--dry-run',
        help=("Find the templates and print them out without commiting them to"
              "the store."),
        action='store_true'
    )

    args = parser.parse_args()

    count, created, updated = importer(args.directory, args.dry_run)

    if len(created):
        print("Created {0}".format(', '.join(created)))

    if len(updated):
        print("Updated {0}".format(', '.join(updated)))

    print("Imported {0} templates".format(count))
