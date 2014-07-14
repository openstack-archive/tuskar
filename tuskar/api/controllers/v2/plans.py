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

from pecan import rest
from wsmeext import pecan as wsme_pecan

from tuskar.api.controllers.v2 import models

LOG = logging.getLogger(__name__)


class PlansController(rest.RestController):
    """REST controller for the Plan class."""

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
