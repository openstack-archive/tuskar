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
import wsme

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

    @wsme.validate(models.Role)
    @wsme_pecan.wsexpose(models.Role,
                         str,
                         body=models.Role,
                         status_code=201)
    def post(self, plan_uuid, transfer_role):
        """Creates a new role.

        :param transfer_role: data submitted by the user
        :type  transfer_role:
            tuskar.api.controllers.v1.models.Role

        :return: created role
        :rtype:  tuskar.api.controllers.v1.models.Role

        :raises: tuskar.common.exception.RoleExists: if a role
                 with the given name exists
        """
        LOG.debug('Creating role: %s' % transfer_role)

        # Persist

        # Package for transfer back to the user
        return transfer_role
