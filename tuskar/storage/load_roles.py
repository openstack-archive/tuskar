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
from os import walk

from tuskar.common import utils
from tuskar.storage.load_utils import create_or_update
from tuskar.storage.load_utils import load_file
from tuskar.storage.load_utils import process_role
from tuskar.storage.stores import MasterSeedStore
from tuskar.storage.stores import ResourceRegistryMappingStore
from tuskar.storage.stores import ResourceRegistryStore
from tuskar.storage.stores import TemplateExtraStore
from tuskar.storage.stores import TemplateStore
from tuskar.templates import parser

MASTER_SEED_NAME = '_master_seed'
RESOURCE_REGISTRY_NAME = '_registry'
ALL_ROLES = ['Compute', 'Controller', 'Swift-Storage', 'Cinder-Storage']
ROLE_EXTRA = ['puppet/hieradata/', 'puppet/manifests/', 'extraconfig']
RESOURCE_REGISTRY = 'overcloud-resource-registry'
SEED = 'overcloud-without-mergepy.yaml'


def role_name_from_path(role_path):
    return path.splitext(path.basename(role_path))[0]


def load_seed(seed_file, resource_registry_path):

    # enforced in CLI
    assert seed_file is not None
    assert resource_registry_path is not None

    all_roles, created, updated = load_roles([], seed_file,
                                             resource_registry_path)
    return created, updated


def load_role(name, file_path, extra_data=None, relative_path=''):
    name = role_name_from_path(file_path) if (name == '') else name
    all_roles, created, updated = load_roles(
        roles=[], seed_file=None,
        resource_registry_path=None, role_extra=extra_data)
    process_role(file_path, name, TemplateStore(), all_roles, created,
                 updated, relative_path)
    return created, updated


def load_roles(roles, seed_file=None, resource_registry_path=None,
               role_extra=None, load_all_roles=False,
               local_tht='/usr/share/openstack-tripleo-heat-templates/'):
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

    :param load_all_roles: Boolean, whether to attempt to gather and load all
           roles ("Compute" "Controller" "Swift-Storage" "Cinder-Storage"
           "Ceph-Storage") encountered within the local_tht directory
    :type  all_roles: Boolean (default False)

    :param local_tht: String, the absolute local path to the
           tripleo-heat-templates directory. Used in conjunction with the
           load_all_roles parameter. Defaults to
           /usr/share/openstack-tripleo-heat-templates/
    :type  local_tht: String

    :return: Summary of the results as a tuple with the total count and then
        the names of the created and updated roles.
    :rtype:  tuple(list, list, list)
    """
    all_roles, created, updated = [], [], []

    def _process_roles(roles, store=None):
        for role_name, role_path in roles:
            process_role(role_path, role_name, store, all_roles, created,
                         updated)

    # This and the next internal method are used when --all
    def _gather_all_local_role_paths():
        local_role_paths = []
        local_role_extra_paths = []
        puppet_role_path = path.join(local_tht, "puppet")
        puppet_roles = True if path.isdir(puppet_role_path) else False
        suffix = "-puppet.yaml" if puppet_roles else ".yaml"
        for role_name in ALL_ROLES:
            if puppet_roles:
                role_path = (path.join(puppet_role_path, role_name.lower())
                             + suffix)
            else:
                role_path = (path.join(local_tht, role_name.lower())
                             + suffix)
            if path.isfile(role_path):
                local_role_paths.append((role_name, role_path))
        for extra_path in ROLE_EXTRA:
            if path.isdir(path.join(local_tht, extra_path)):
                for dirpath, dirnames, filenames in walk(path.join(
                        local_tht, extra_path)):
                    for filename in filenames:
                        local_role_extra_paths.append(path.join(
                                                      dirpath, filename))
        registry = path.join(local_tht, (RESOURCE_REGISTRY + suffix))
        seed = path.join(local_tht, SEED)
        return local_role_paths, local_role_extra_paths, registry, seed

    if load_all_roles:
        roles, role_extra, registry, seed = _gather_all_local_role_paths()
        resource_registry_path = (registry if not resource_registry_path
                                  else resource_registry_path)
        seed_file = seed if not seed_file else seed_file
    else:
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
            # skip adding if template has already been stored as a role
            if (complete_path in role_paths):
                continue

            if (entry.is_filename()):
                process_role(complete_path, entry.filename, mapping_store,
                             None, created, updated)
            else:
                # if entry is not a filename, (is an alias) add to mappings
                create_or_update(entry.filename, entry.alias, mapping_store)

    return all_roles, created, updated
