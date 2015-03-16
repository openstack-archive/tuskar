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

from os import path

from tuskar.common import utils
from tuskar.storage.load_utils import load_file
from tuskar.storage.load_utils import process_role
from tuskar.storage.stores import MasterSeedStore
from tuskar.storage.stores import ResourceRegistryMappingStore
from tuskar.storage.stores import ResourceRegistryStore
from tuskar.storage.stores import TemplateExtraStore
from tuskar.templates import parser

MASTER_SEED_NAME = '_master_seed'
RESOURCE_REGISTRY_NAME = '_registry'


def role_name_from_path(role_path):
    return path.splitext(path.basename(role_path))[0]


def load_roles(roles, seed_file=None, resource_registry_path=None,
               role_extra=None):
    """Given a list of roles files import them into the
    add any to the store. TemplateStore.

    The returned tuple contains all the role names and then the names split
    over where were created and updated. On a dry run the first item will
    contain all of the roles found while the second two will be empty lists as
    no files were updated or created.

    :param roles: A list of yaml files (as strings)
    :type  roles: [str]

    :param seed_file: full path to the template seed that should be used for
           plan master templates
    :type  seed_file: str

    :param resource_registry_path: path to the Heat environment which
           declares the custom types for Tuskar roles.
    :type  resource_registry_path: str

    :param role_extra: A list of yaml files (as strings) that may be consumed
           (referenced) by any of the role files.
    :type  roles: [str]

    :return: Summary of the results as a tuple with the total count and then
        the names of the created and updated roles.
    :rtype:  tuple(list, list, list)
    """
    all_roles, created, updated = [], [], []

    def _process_roles(roles, store=None):
        for role_name, role_path in roles:
            process_role(role_path, role_name, store, all_roles, created,
                         updated)

    roles = [(role_name_from_path(r), r) for r in roles]
    _process_roles(roles)

    template_extra_store = TemplateExtraStore()
    if role_extra is not None:
        role_extra = [(utils.resolve_role_extra_name_from_path(re), re)
                      for re in role_extra]
        _process_roles(role_extra, template_extra_store)

    if seed_file is not None:
        process_role(seed_file, MASTER_SEED_NAME,
                     MasterSeedStore(), all_roles, created, updated)

    if resource_registry_path is not None:
        process_role(resource_registry_path, RESOURCE_REGISTRY_NAME,
                     ResourceRegistryStore(), all_roles, created, updated)

        contents = load_file(resource_registry_path)
        parsed_env = parser.parse_environment(contents)

        mapping_store = ResourceRegistryMappingStore()
        dirname = path.dirname(resource_registry_path)
        role_paths = [r[1] for r in roles]
        for entry in parsed_env.registry_entries:
            complete_path = path.join(dirname, entry.filename)
            # skip adding if entry is not a filename (is another alias) or
            # if template has already been stored as a role
            if (not entry.is_filename() or complete_path in role_paths):
                continue

            process_role(complete_path, entry.filename, mapping_store,
                         None, created, updated)

    return all_roles, created, updated
