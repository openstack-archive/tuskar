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
from wsme.types import UnsetType
from wsmeext import pecan as wsme_pecan

from tuskar.api.controllers.v2 import models
from tuskar.api.controllers.v2 import roles
from tuskar.common.exception import PlanNotFound
from tuskar.manager.plan import PlansManager
from tuskar.storage.exceptions import UnknownUUID


LOG = logging.getLogger(__name__)


class PlansController(rest.RestController):
    """REST controller for the Plan class."""

    _custom_actions = {'templates': ['GET']}

    roles = roles.RolesController()

    @wsme_pecan.wsexpose([models.Plan])
    def get_all(self):
        """Returns all plans.

        An empty list is returned if no plans are present.

        :return: list of plans; empty list if none are found
        :rtype:  list of tuskar.api.controllers.v2.models.Plan
        """
        LOG.debug('Retrieving all plans')
        manager = PlansManager()
        all_plans = manager.list_plans()
        if len(all_plans) > 0:
            transfer_plans = [models.Plan.from_tuskar_model(p)
                              for p in all_plans]
        else:
            transfer_plans = []
        return transfer_plans

    @wsme_pecan.wsexpose(models.Plan, str)
    def get_one(self, plan_uuid):
        """Returns a specific plan.

        An exception is raised if no plan is found with the
        given UUID.

        :param plan_uuid: identifies the plan being fetched
        :type  plan_uuid: str

        :return: matching plan
        :rtype:  tuskar.api.controllers.v2.models.Plan

        :raises: tuskar.common.exception.PlanNotFound if there
                 is no plan with the given UUID
        """
        LOG.debug('Retrieving plan with UUID: %s' % plan_uuid)
        manager = PlansManager()
        try:
            found = manager.retrieve_plan(plan_uuid)
        except UnknownUUID:
            LOG.exception('Could not retrieve plan: %s' % plan_uuid)
            raise PlanNotFound()
        transfer = models.Plan.from_tuskar_model(found)
        return transfer

    @wsme_pecan.wsexpose(None, str, status_code=204)
    def delete(self, plan_uuid):
        """Deletes the given plan.

        :param plan_uuid: identifies the plan being deleted
        :type  plan_uuid: str

        :raises: tuskar.common.exception.PlanNotFound if there
                 is no plan with the given UUID
        """

        LOG.debug('Deleting plan with UUID: %s' % plan_uuid)
        manager = PlansManager()
        try:
            manager.delete_plan(plan_uuid)
        except UnknownUUID:
            LOG.exception('Could not delete plan: %s' % plan_uuid)
            raise PlanNotFound()

    @wsme_pecan.wsexpose(models.Plan,
                         body=models.Plan,
                         status_code=201)
    def post(self, transfer_plan):
        """Creates a new plan.

        :param transfer_plan: data submitted by the user
        :type  transfer_plan:
            tuskar.api.controllers.v1.models.Plan

        :return: created plan
        :rtype:  tuskar.api.controllers.v1.models.Plan

        :raises: tuskar.common.exception.PlanExists: if a plan
                 with the given name exists
        """
        LOG.debug('Creating plan: %s' % transfer_plan)

        # We don't want the wsme types bleed into the rest of Tuskar, so
        # explicitly set to None if it wasn't specified.
        description = transfer_plan.description
        if isinstance(description, UnsetType):
            description = None

        manager = PlansManager()
        created = manager.create_plan(transfer_plan.name,
                                      description)
        transfer = models.Plan.from_tuskar_model(created)
        return transfer

    @pecan.expose()
    def templates(self, plan_uuid):
        return plan_uuid

    @wsme.validate(models.Plan)
    @wsme_pecan.wsexpose(models.Plan,
                         str,
                         body=[models.ParameterValue],
                         status_code=201)
    def patch(self, plan_uuid, param_list):
        """Patches existing plan.

        :return: patched plan
        :rtype:  tuskar.api.controllers.v1.models.Plan
        """
        manager = PlansManager()
        params = [p.to_tuskar_model() for p in param_list]
        updated_plan = manager.set_parameter_values(plan_uuid, params)
        transfer_plan = models.Plan.from_tuskar_model(updated_plan)
        return transfer_plan
