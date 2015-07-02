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

from oslo_config import cfg

from tuskar.common import service
from tuskar.storage import delete_roles as dr


def _print_names(message, names):
    print("{0}: \n    {1}".format(message, '\n    '.join(names)))

cfg.CONF.register_cli_opt(cfg.BoolOpt('dryrun', default=False))

cfg.CONF.register_cli_opt(cfg.MultiStrOpt(
    'uuid', short='u', help='List of role uuid to delete'))

cfg.CONF.register_cli_opt(cfg.BoolOpt(
    'all', default=False,
    help='If specified, all roles will be deleted; overrides the '
         '--uuids argument'))


def main(argv=None):
    if argv is None:
        argv = sys.argv

    service.prepare_service(argv)

    if not cfg.CONF.uuid and not cfg.CONF.all:
        sys.stderr.write(
            'Either specific roles must be specified using the --uuid '
            'argument or --all must be specified\n')
        sys.exit(1)

    if cfg.CONF.uuid:
        deleted = dr.delete_roles(cfg.CONF.uuid, noop=cfg.CONF.dryrun)
    else:
        deleted = dr.delete_all_roles(noop=cfg.CONF.dryrun)

    if len(deleted):
        _print_names("Deleted", deleted)
