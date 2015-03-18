#!/usr/bin/env python
#
# Copyright 2015 Red Hat
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
from tuskar.storage.delete_roles import delete_roles


def _print_names(message, names):
    print("{0}: \n    {1}".format(message, '\n    '.join(names)))

cfg.CONF.register_cli_opt(cfg.BoolOpt('dryrun', short='n', default=False))

cfg.CONF.register_cli_opt(cfg.ListOpt(
    'uuids', help='List of role uuid to delete'))


def main(argv=None):
    if argv is None:
        argv = sys.argv

    index = argv.index('--uuids')
    service.prepare_service(argv[:index])
    roles = argv[index + 1:]

    deleted = delete_roles(roles, noop=cfg.CONF.dryrun)

    if len(deleted):
        _print_names("Deleted", deleted)
