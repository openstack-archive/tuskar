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

import logging

import pecan
from pecan import rest
import wsme
from wsmeext import pecan as wsme_pecan

from tuskar.api.controllers.v1 import models


LOG = logging.getLogger(__name__)


class OvercloudRolesController(rest.RestController):
    """REST controller for the OvercloudRole class."""

    @wsme.validate(models.OvercloudRole)
    @wsme_pecan.wsexpose(models.OvercloudRole,
                         body=models.OvercloudRole,
                         status_code=201)
    def post(self, transfer_role):
        """Creates a new overcloud role.

        :param transfer_role: data submitted by the user
        :type  transfer_role:
               tuskar.api.controllers.v1.models.OvercloudRole

        :return: created role
        :rtype:  tuskar.api.controllers.v1.models.OvercloudRole

        :raises: tuskar.common.exception.OvercloudRoleExists: if an overcloud
                 role with the given name exists
        """

        LOG.debug('Creating overcloud role: %s' % transfer_role)

        # Persist to the database
        db_role = transfer_role.to_db_model()
        result = pecan.request.dbapi.create_overcloud_role(db_role)

        # Package for transfer back to the user
        saved_role = models.OvercloudRole.from_db_model(result)

        return saved_role

    @wsme.validate(models.OvercloudRole)
    @wsme_pecan.wsexpose(models.OvercloudRole,
                         int,
                         body=models.OvercloudRole)
    def put(self, role_id, role_delta):
        """Updates an existing overcloud role.

        :param role_id: identifies the role being deleted
        :type  role_id: int

        :param role_delta: contains only values that are to be affected
               by the update operation
        :type  role_delta:
               tuskar.api.controllers.v1.models.OvercloudRole

        :return: role with updated values
        :rtype:  tuskar.api.controllers.v1.models.OvercloudRole

        :raises: tuskar.common.exception.OvercloudRoleNotFound if there
                 is no role with the given ID
        """

        LOG.debug('Updating overcloud role: %s' % role_id)

        # ID is in the URL so make sure it's in the transfer object
        # before translation
        role_delta.id = role_id

        db_delta = role_delta.to_db_model(omit_unset=True)

        # Will raise a not found if there is no role with the ID
        updated = pecan.request.dbapi.update_overcloud_role(db_delta)

        return updated

    @wsme_pecan.wsexpose(None, int, status_code=204)
    def delete(self, role_id):
        """Deletes the given overcloud role.

        :param role_id: identifies the role being deleted
        :type  role_id: int

        :raises: tuskar.common.exception.OvercloudRoleNotFound if there
                 is no role with the given ID
        """

        LOG.debug('Deleting overcloud role with ID: %s' % role_id)
        pecan.request.dbapi.delete_overcloud_role_by_id(role_id)

    @wsme_pecan.wsexpose(models.OvercloudRole, int)
    def get_one(self, role_id):
        """Returns a specific overcloud role.

        An exception is raised if no overcloud role is found with the
        given ID.

        :param role_id: identifies the role being deleted
        :type  role_id: int

        :return: matching resource role
        :rtype:  tuskar.api.controllers.v1.models.OvercloudRole

        :raises: tuskar.common.exception.OvercloudRoleNotFound if there
                 is no role with the given ID
        """

        LOG.debug('Retrieving overcloud role with ID: %s' % role_id)
        db_role = pecan.request.dbapi.get_overcloud_role_by_id(role_id)
        transfer_role = models.OvercloudRole.from_db_model(db_role)
        return transfer_role

    @wsme_pecan.wsexpose([models.OvercloudRole])
    def get_all(self):
        """Returns all overcloud roles.

        An empty list is returned if no overcloud roles are present.

        :return: list of roles; empty list if none are found
        :rtype:  list of tuskar.api.controllers.v1.models.OvercloudRole
        """
        LOG.debug('Retrieving all overcloud roles')
        db_roles = pecan.request.dbapi.get_overcloud_roles()
        transfer_roles = [models.OvercloudRole.from_db_model(c)
                          for c in db_roles]
        return transfer_roles
