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

import logging

from pecan import rest
from wsmeext import pecan as wsme_pecan

from tuskar.api.controllers.v2 import models

LOG = logging.getLogger(__name__)


class RolesController(rest.RestController):
    """REST controller for the Role class."""

    @wsme_pecan.wsexpose([models.Role])
    def get_all(self):
        """Returns all roles.

        An empty list is returned if no roles are present.

        :return: list of roles; empty list if none are found
        :rtype:  list of tuskar.api.controllers.v2.models.Role
        """
        LOG.debug('Retrieving all roles')
        roles = [
            models.Role(**{
                'uuid': '42',
                'name': 'foo',
            }),
        ]
        return roles

    @wsme_pecan.wsexpose(models.Plan,
                         str,
                         body=models.Role,
                         status_code=201)
    def post(self, plan_uuid, role):
        """Adds a new role to plan.

        :param plan_uuid: identifies the plan
        :type  plan_uuid: str

        :param role: the role to be added to plan
        :type  role: tuskar.api.controllers.v2.models.Role

        :return: modified plan
        :rtype:  tuskar.api.controllers.v2.models.Plan
        """
        LOG.debug('Adding role: %s' % role.uuid)

        # Persist

        # Package for transfer back to the user
        plan = models.Plan(**{
            'uuid': '42',
            'name': 'foo',
            'roles': [role]
        })
        return plan

    @wsme_pecan.wsexpose(models.Plan,
                         str,
                         str,
                         str)
    def delete(self, plan_uuid, role_name, role_version):
        """Removes a role from given plan.

        :param plan_uuid: identifies the plan
        :type  plan_uuid: str

        :param role_name: identifies the role to be deleted from plan
        :type  role_name: str

        :param role_version: identifies the version of role to be deleted
        :type  role_version: str
       """

        plan = models.Plan(**{
            'uuid': '42',
            'name': 'foo',
        })
        return plan
