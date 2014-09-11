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

import sys

from oslo.config import cfg

from tuskar.common import service
from tuskar.storage.load_roles import load_roles


def _print_names(message, names):
    print("{0}: \n    {1}".format(message, '\n    '.join(names)))


cfg.CONF.register_cli_opt(cfg.BoolOpt('dry-run'))
seed_help = ('Full path to the template that should be loaded '
             'as the master seed')
cfg.CONF.register_cli_opt(cfg.StrOpt('master-seed', dest='master_seed',
                                     help=seed_help))
cfg.CONF.register_cli_opt(cfg.StrOpt('directory', positional=True))


def main(argv=None):

    if argv is None:
        argv = sys.argv

    service.prepare_service(argv)

    all_roles, created, updated = load_roles(cfg.CONF.directory,
                                             seed_file=cfg.CONF.master_seed,
                                             dry_run=cfg.CONF.dry_run)

    if len(created):
        _print_names("Created", created)

    if len(updated):
        _print_names("Updated", updated)

    if not cfg.CONF.dry_run:
        print("Imported {0} roles".format(len(all_roles)))
    else:
        _print_names("Found", all_roles)
        print("Imported 0 roles")
