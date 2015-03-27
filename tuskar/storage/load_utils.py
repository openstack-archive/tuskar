# -*- encoding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from tuskar.storage.exceptions import UnknownName
from tuskar.storage.stores import TemplateStore


def load_file(role_path):
    with open(role_path) as role_file:
        return role_file.read()


def create_or_update(name, contents, store=None, relative_path=''):
    if store is None:
        store = TemplateStore()
    try:
        role = store.retrieve_by_name(name)
        if role.contents != contents:
            role = store.update(role.uuid, contents, relative_path)

        return False, role
    except UnknownName:
        return True, store.create(name, contents, relative_path)


def process_role(role_path, role_name, store, all_roles, created, updated,
                 relative_path=''):
    contents = load_file(role_path)
    role_created, _ = create_or_update(role_name, contents, store,
                                       relative_path)

    if all_roles is not None:
        all_roles.append(role_name)

    if role_created:
        created.append(role_name)
    else:
        updated.append(role_name)
