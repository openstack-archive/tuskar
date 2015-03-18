
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

from tuskar.common.exception import OvercloudRoleInUse
from tuskar.manager.plan import PlansManager
from tuskar.storage.exceptions import UnknownUUID
from tuskar.storage.stores import DeploymentPlanStore
from tuskar.storage.stores import TemplateStore
from tuskar.templates import parser


def _check_roles_exist(role_ids):
    store = TemplateStore()
    for i in role_ids:
        try:
            store.retrieve(i)
        except UnknownUUID:
            sys.stderr.write("No role with id %s " % i)
            raise


def _check_roles_in_use(role_ids):
    manager = PlansManager()
    plan_list = manager.list_plans()
    plan_store = DeploymentPlanStore()
    for plan in plan_list:
        db_plan = plan_store.retrieve(plan.uuid)
        environment = parser.parse_environment(
            db_plan.environment_file.contents
        )
        roles_in_use = (
            [role.uuid for role in manager._find_roles(environment)])
        intersection = set(roles_in_use) & set(role_ids)
        if intersection:
            raise OvercloudRoleInUse(name=", ".join(intersection))


def _delete_role(role_id):
    TemplateStore().delete(role_id)


def delete_roles(role_ids=None, noop=False):
    deleted = []
    # if any of the roles are in use, or invalid, do nothing
    _check_roles_in_use(role_ids)
    _check_roles_exist(role_ids)
    if noop:
        role_ids.append("No deletions, dryrun")
        return role_ids
    else:
        for i in role_ids:
            _delete_role(i)
            deleted.append(i)
        return deleted
