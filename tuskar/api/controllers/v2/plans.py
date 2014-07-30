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

from tuskar.api.controllers.v2 import models
from tuskar.api.controllers.v2 import roles

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
        plans = [
            models.Plan(**{
                'uuid': '42',
                'name': 'foo',
            }),
        ]
        return plans

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
        plan = models.Plan(**{
            'uuid': '42',
            'name': 'foo',
        })
        return plan

    @wsme_pecan.wsexpose(None, str, status_code=204)
    def delete(self, plan_uuid):
        """Deletes the given plan.

        :param plan_uuid: identifies the plan being deleted
        :type  plan_uuid: str

        :raises: tuskar.common.exception.PlanNotFound if there
                 is no plan with the given UUID
        """

        LOG.debug('Deleting plan with UUID: %s' % plan_uuid)

        # delete plan here

    @wsme.validate(models.Plan)
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

        # Persist

        # Package for transfer back to the user
        return transfer_plan

    @pecan.expose()
    def templates(self, plan_uuid):
        return plan_uuid

    @wsme.validate(models.Plan)
    @wsme_pecan.wsexpose(models.Plan,
                         str,
                         body=models.Plan,
                         status_code=201)
    def patch(self, plan_uuid, transfer_plan):
        """Patches existing plan.

        :param transfer_plan: data submitted by the user
        :type  transfer_plan:
            tuskar.api.controllers.v1.models.Plan

        :return: patched plan
        :rtype:  tuskar.api.controllers.v1.models.Plan
        """
        LOG.debug('Patching plan: %s' % transfer_plan)

        # Package for transfer back to the user
        return transfer_plan
