#!/usr/bin/env python
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
from tuskar.storage.load_roles import load_seed


def _print_names(message, names):
    print("{0}: \n    {1}".format(message, '\n    '.join(names)))


seed_help = ('Full path to the template that should be loaded '
             'as the master seed')
resource_registry_help = ('Path to the Heat environment file which maps the'
                          'custom resource types to template paths.')
cfg.CONF.register_cli_opt(cfg.StrOpt('master-seed', dest='master_seed',
                                     help=seed_help))
cfg.CONF.register_cli_opt(cfg.StrOpt('resource-registry',
                                     dest='resource_registry',
                                     help=resource_registry_help))


def main(argv=None):

    if argv is None:
        argv = sys.argv

    service.prepare_service(argv)

    if not cfg.CONF.master_seed or not cfg.CONF.resource_registry:
        sys.stderr.write("You must specify both `master-seed` and "
                         "`resource-registry`.")
        sys.exit(1)

    created, updated = load_seed(
        seed_file=cfg.CONF.master_seed,
        resource_registry_path=cfg.CONF.resource_registry)

    if len(created):
        _print_names("Created", created)

    if len(updated):
        _print_names("Updated", updated)
