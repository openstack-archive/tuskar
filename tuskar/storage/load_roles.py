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
from tuskar.storage.exceptions import UnknownName
from tuskar.storage.stores import MasterSeedStore
from tuskar.storage.stores import ResourceRegistryMappingStore
from tuskar.storage.stores import ResourceRegistryStore
from tuskar.storage.stores import TemplateExtraStore
from tuskar.storage.stores import TemplateStore
from tuskar.templates import parser

MASTER_SEED_NAME = '_master_seed'
RESOURCE_REGISTRY_NAME = '_registry'


def _load_file(role_path):

    with open(role_path) as role_file:
        return role_file.read()


def _create_or_update(name, contents, store=None):

    if store is None:
        store = TemplateStore()

    try:
        role = store.retrieve_by_name(name)

        if role.contents != contents:
            role = store.update(role.uuid, contents)

        return False, role
    except UnknownName:
        return True, store.create(name, contents)


def role_name_from_path(role_path):
    return path.splitext(path.basename(role_path))[0]


def load_roles(roles, seed_file=None, resource_registry_path=None,
               dry_run=False, role_extra=None):
    """Given a list of roles files import them into the
    add any to the store. TemplateStore. When dry_run=True is
    passed, run through the roles but don't

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
        for name, role_path in roles:

            contents = _load_file(role_path)
            all_roles.append(name)

            if dry_run:
                continue

            role_created, _ = _create_or_update(name, contents, store)

            if role_created:
                created.append(name)
            else:
                updated.append(name)

    roles = [(role_name_from_path(r), r) for r in roles]
    _process_roles(roles)
    template_extra_store = TemplateExtraStore()
    if role_extra is not None:
        role_extra = [(utils.resolve_role_extra_name_from_path(re), re)
                      for re in role_extra]
        _process_roles(role_extra, template_extra_store)

    if seed_file is not None:
        contents = _load_file(seed_file)
        seed_created, role = _create_or_update(MASTER_SEED_NAME, contents,
                                               store=MasterSeedStore())
        all_roles.append(MASTER_SEED_NAME)

        if seed_created:
            created.append(MASTER_SEED_NAME)
        else:
            updated.append(MASTER_SEED_NAME)

    if resource_registry_path is not None:
        contents = _load_file(resource_registry_path)
        store = ResourceRegistryStore()
        registry_created, role = _create_or_update(RESOURCE_REGISTRY_NAME,
                                                   contents,
                                                   store=store)
        all_roles.append(RESOURCE_REGISTRY_NAME)
        if registry_created:
            created.append(RESOURCE_REGISTRY_NAME)
        else:
            updated.append(RESOURCE_REGISTRY_NAME)

        parsed_env = parser.parse_environment(contents)

        dirname = path.dirname(resource_registry_path)
        for entry in parsed_env.registry_entries:
            complete_path = dirname + '/' + entry.filename
            # skip adding if entry is not a filename (is another alias) or
            # if template has already been stored as a role
            if (not entry.is_filename() or [afile for afile, apath in roles
                                            if apath == complete_path]):
                continue

            store = ResourceRegistryMappingStore()
            flag, role = _create_or_update(entry.filename,
                                           _load_file(complete_path),
                                           store=store)

    return all_roles, created, updated
