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

from os import listdir
from os import path

from tuskar.storage.exceptions import UnknownName
from tuskar.storage.stores import MasterSeedStore
from tuskar.storage.stores import TemplateStore


MASTER_SEED_NAME = '_master_seed'


def _list_roles(directory):
    """Scan a directory and yield a tuple for all the roles containing the
    role name and the full path to the role.
    """

    if not path.isdir(directory):
        raise ValueError("The given path is not a valid directory.")

    directory = path.abspath(directory)

    for filename in listdir(directory):

        if not filename.endswith("yaml") and not filename.endswith("yml"):
            continue

        role_name = path.splitext(filename)[0]
        yield role_name, path.join(directory, filename)


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


def load_roles(directory, seed_file=None, dry_run=False):
    """Given a directory path, import the YAML role files into the
    TemplateStore. When dry_run=True is passed, run through the roles but don't
    add any to the store.

    The returned tuple contains all the role names and then the names split
    over where were created and updated. On a dry run the first item will
    contain all of the roles found while the second two will be empty lists as
    no files were updated or created.

    :param directory: Directory name containing the roles
    :type  directory: str

    :param seed_file: full path to the template seed that should be used for
           plan master templates
    :type  seed_file: str

    :return: Summary of the results as a tuple with the total count and then
        the names of the created and updated roles.
    :rtype:  tuple(list, list, list)
    """

    all_roles, created, updated = [], [], []

    roles = _list_roles(directory)

    for name, role_path in roles:

        contents = _load_file(role_path)
        all_roles.append(name)

        if dry_run:
            continue

        role_created, _ = _create_or_update(name, contents)

        if role_created:
            created.append(name)
        else:
            updated.append(name)

    if seed_file is not None:
        contents = _load_file(seed_file)
        seed_created, role = _create_or_update(MASTER_SEED_NAME, contents,
                                               store=MasterSeedStore())
        all_roles.append(MASTER_SEED_NAME)

        if seed_created:
            created.append(MASTER_SEED_NAME)
        else:
            updated.append(MASTER_SEED_NAME)

    return all_roles, created, updated
