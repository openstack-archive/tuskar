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


from oslo_log import log as logging
from pecan import rest
from wsmeext import pecan as wsme_pecan

from tuskar.api.controllers.v2 import models
from tuskar.common import exception
from tuskar.common import utils
from tuskar.manager.plan import PlansManager
from tuskar.manager.role import RoleManager
from tuskar.storage import exceptions as storage_exceptions


LOG = logging.getLogger(__name__)


class RolesController(rest.RestController):
    """REST controller for the Role class."""

    _custom_actions = {'extra_data': ['GET']}

    @wsme_pecan.wsexpose([models.Role])
    def get_all(self):
        """Returns all roles.

        An empty list is returned if no roles are present.

        :return: list of roles; empty list if none are found
        :rtype:  list of tuskar.api.controllers.v2.models.Role
        """
        LOG.debug('Retrieving all roles')
        manager = RoleManager()
        all_roles = manager.list_roles(only_latest=False)
        transfer_roles = [models.Role.from_tuskar_model(r) for r in all_roles]
        return transfer_roles

    @wsme_pecan.wsexpose({str: str}, str)
    def extra_data(self, role_uuid):
        """Retrieve the extra data files associated with a given role.

        :param role_uuid: identifies the role
        :type  role_uuid: str

        :return: a dict where keys are filenames and values are their contents
        :rtype:  dict

        This method will retrieve all stored role_extra records (these are
        created at the same time that the Roles are, by using --role-extra
        parameter to tuskar-load-roles).

        The internal representation for a given role-extra file encodes the
        file extension into the name. For instance 'hieradata/compute.yaml'
        is stored as 'extra_compute_yaml'.

        The given role's template is searched for 'get_file' directives and
        then matched against the stored role-extra records (based on their
        name... e.g. 'extra_controller_yaml' we look for 'controller.yaml'
        after a get_file directive).

        This method thus returns all the matched role-extra files for the
        given role. The keys will include the relative path if one is
        used in the role template:
        {
            "hieradata/common.yaml": "CONTENTS",
            "hieradata/controller.yaml": "CONTENTS",
            "hieradata/object.yaml": "CONTENTS"
        }

        """
        manager = RoleManager()
        db_role = manager.retrieve_db_role_by_uuid(role_uuid)
        db_role_extra = manager.retrieve_db_role_extra()
        role_extra_paths = utils.resolve_template_extra_data(
            db_role, db_role_extra)
        return manager.template_extra_data_for_output(role_extra_paths)

    @wsme_pecan.wsexpose(models.Plan,
                         str,
                         body=models.Role,
                         status_code=201)
    def post(self, plan_uuid, role):
        """Adds a new role to plan.

        :param plan_uuid: identifies the plan
        :type  plan_uuid: str

        :param role: identifies the role to add
        :type  role: tuskar.api.controllers.v2.models.Role

        :return: modified plan
        :rtype:  tuskar.api.controllers.v2.models.Plan

        :raises: tuskar.common.exception.PlanAlreadyHasRole if the role has
            already been added to the plan.
        """
        LOG.debug('Adding role: %(role_uuid)s to plan: %(plan_uuid)s' %
                  {'role_uuid': role.uuid, 'plan_uuid': plan_uuid})
        manager = PlansManager()
        try:
            updated_plan = manager.add_role_to_plan(plan_uuid, role.uuid)
        except ValueError:
            LOG.debug('The role has already been added to the plan.')
            raise exception.PlanAlreadyHasRole(
                plan_uuid=plan_uuid,
                role_uuid=role.uuid
            )
        except storage_exceptions.UnknownUUID as e:
            LOG.debug(('Either the plan UUID {0} or role UUID {1} could not be'
                       'found').format(plan_uuid, role.uuid))
            raise exception.NotFound(
                message=str(e))
        transfer_plan = models.Plan.from_tuskar_model(updated_plan)
        return transfer_plan

    @wsme_pecan.wsexpose(models.Plan,
                         str,
                         str)
    def delete(self, plan_uuid, role_uuid):
        """Removes a role from given plan.

        :param plan_uuid: identifies the plan
        :type  plan_uuid: str

        :param role_uuid: identifies the role to be deleted from plan
        :type  role_uuid: str
        """
        LOG.debug('Removing role: %(role_uuid)s from plan: %(plan_uuid)s' %
                  {'role_uuid': role_uuid, 'plan_uuid': plan_uuid})
        manager = PlansManager()
        try:
            updated_plan = manager.remove_role_from_plan(plan_uuid, role_uuid)
        except storage_exceptions.UnknownUUID as e:
            LOG.debug(('Either the plan UUID {0} or role UUID {1} could not be'
                       'found').format(plan_uuid, role_uuid))
            raise exception.NotFound(
                message=str(e))
        transfer_plan = models.Plan.from_tuskar_model(updated_plan)
        return transfer_plan
