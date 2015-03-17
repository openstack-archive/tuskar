#!/usr/bin/env python
#
# Copyright 2015 Red Hat
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
from tuskar.storage.load_roles import load_role


def _print_names(message, names):
    print("{0}: \n    {1}".format(message, '\n    '.join(names)))

cfg.CONF.register_cli_opt(cfg.StrOpt('name', short='n', dest='name'))
cfg.CONF.register_cli_opt(cfg.StrOpt(
    'filepath', dest='file_path', short='f'))
cfg.CONF.register_cli_opt(cfg.StrOpt('relative-path', dest='relative_path'))
cfg.CONF.register_cli_opt(cfg.MultiStrOpt('extra-data', short='e'))


def main(argv=None):
    if argv is None:
        argv = sys.argv

    service.prepare_service(argv)
    if not cfg.CONF.file_path:
        sys.stderr.write("You must specify the path to the main template "
                         "which defines this role.")
        sys.exit(1)

    name = cfg.CONF.name if cfg.CONF.name else ''
    relative_path = cfg.CONF.relative_path if cfg.CONF.relative_path else ''
    created, updated = load_role(name, cfg.CONF.file_path,
                                 extra_data=cfg.CONF.extra_data,
                                 relative_path=relative_path)

    if len(created):
        _print_names("Created", created)

    if len(updated):
        _print_names("Updated", updated)
