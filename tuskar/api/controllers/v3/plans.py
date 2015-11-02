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
#import tripleo_common
import wsme
from wsme.types import UnsetType
from wsmeext import pecan as wsme_pecan

from tuskar.common import exception


LOG = logging.getLogger(__name__)


class PlansController(rest.RestController):
    """REST controller for the Plan class."""

    _custom_actions = {'deploy': ['POST'],
                       'parameters': ['GET', 'POST'],
                       'resource_types': ['GET', 'POST'],
                       'roles': ['GET'],
                       'validate': ['GET']}

    # TEMPORARY TEST PLANS
    global test_plan
    test_plan = {
        'plan_file_1': 'contents of plan file 1',
        'plan_file_2': 'contents of plan file 2',
        'plan_file_3': 'contents of plan file 3',
    }
    
    @wsme_pecan.wsexpose([{str: str}])
    def get_all(self):
        """Returns all plans.

        An empty list is returned if no plans are present.

        :return: list of plans; empty list if none are found
        :rtype:  list of tuskar.api.controllers.v2.models.Plan
        """
        LOG.debug('Retrieving all plans')
        #return tripleo_common.get_plans
        return [test_plan]

    @wsme_pecan.wsexpose({str: str}, str)
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
        #try:
        #    found = tripleo_common.get_plan(plan_uuid)
        #except SomeException:
        #    LOG.exception('Could not retrieve plan: %s' % plan_uuid)
        #    raise exception.PlanNotFound()
        #return found
        if plan_uuid == 'overcloud':
            return test_plan
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose(None, str, status_code=204)
    def delete(self, plan_uuid):
        """Deletes the given plan.

        :param plan_uuid: identifies the plan being deleted
        :type  plan_uuid: str

        :raises: tuskar.common.exception.PlanNotFound if there
                 is no plan with the given UUID
        """

        LOG.debug('Deleting plan with UUID: %s' % plan_uuid)
        #try:
        #    tripleo_common.delete_plan(plan_uuid)
        #except SomeException:
        #    LOG.exception('Could not delete plan: %s' % plan_uuid)
        #    raise exception.PlanNotFound()
        if not plan_uuid == 'overcloud':
            raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str},
                         body={str: str},
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
        #try:
            # created = tripleo_common.create_plan(transfer_plan)
        #except SomeException
        #    LOG.exception('Plan already exists with this name')
        #    raise exception.PlanExists(transfer_plan.name)
        #return created
        if transfer_plan['name'] != 'overcloud':
            raise exception.PlanExists(transfer_plan['name'])
        return test_plan
    
    @wsme_pecan.wsexpose({str: str},
                         str,
                         body={str: str},
                         status_code=201)
    def patch(self, plan_uuid, transfer_plan):
        """Patches existing plan.

        :return: patched plan
        :rtype:  tuskar.api.controllers.v1.models.Plan
        """
        LOG.debug('Updating plan: %s' % transfer_plan)

        #try:
        #    updated = tripleo_common.update_plan(plan_uuid, plan_files)
        #except SomeException
        #    LOG.exception('Could not patch plan: %s' % plan_uuid)
        #    raise exception.PlanNotFound()
        #return updated
        if plan_uuid == 'overcloud':
            return test_plan
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str},
                         str,
                         status_code=201)
    def get_parameters(self, plan_uuid):
        """Patches existing plan.

        :return: plan parameters
        :rtype:  tuskar.api.controllers.v1.models.Plan
        """
        LOG.debug('Getting plan parameters: %s' % plan_uuid)

        #try:
        #    parameters = tripleo_common.get_parameters(plan_uuid)
        #except SomeException
        #    LOG.exception('Could not find plan parameters: %s' % plan_uuid)
        #    raise exception.PlanNotFound()
        #return parameters
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str},
                         str,
                         body={str: str},
                         status_code=201)
    def post_parameters(self, plan_uuid, transfer_parameters):
        """Patches existing plan.

        :return: plan parameters
        :rtype:  tuskar.api.controllers.v1.models.Plan
        """
        LOG.debug('Updating plan parameters: %s' % transfer_parameters)

        #try:
        #    params = tripleo_common.update_parameters(plan_uuid, transfer_parameters)
        #except SomeException
        #    LOG.exception('Could not update plan parameters: %s' % plan_uuid)
        #    raise exception.PlanNotFound()
        #return params
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str},
                         str,
                         status_code=201)
    def get_resource_types(self, plan_uuid):
        """Patches existing plan.

        :return: plan resource types
        :rtype:  tuskar.api.controllers.v1.models.Plan
        """
        LOG.debug('Getting plan resource types: %s' % plan_uuid)

        #try:
        #    resource_types = tripleo_common.get_resource_types(plan_uuid)
        #except SomeException
        #    LOG.exception('Could not find plan resource types: %s' % plan_uuid)
        #    raise exception.PlanNotFound()
        #return resource_types
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str},
                         str,
                         body={str: str},
                         status_code=201)
    def post_resource_types(self, plan_uuid, transfer_resource_types):
        """Patches existing plan.

        :return: plan resource types
        :rtype:  tuskar.api.controllers.v1.models.Plan
        """
        LOG.debug('Updating plan resource types: %s' % transfer_resource_types)

        #try:
        #    params = tripleo_common.update_resource_types(plan_uuid, transfer_resource_types)
        #except SomeException
        #    LOG.exception('Could not update plan resource types: %s' % plan_uuid)
        #    raise exception.PlanNotFound()
        #return params
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose([{str: str}], str)
    def roles(self, plan_uuid):
        """Returns the roles for a given plan.

        :return: list of roles
        :rtype:  list
        """
        LOG.debug('Retrieving roles for plan: %s' % plan_uuid)

        #try:
        #    roles = tripleo_common.get_plan_roles(plan_uuid)
        #except SomeException
        #    LOG.exception('Could not retrieve roles for plan: %s' %
        #                  plan_uuid)
        #    raise exception.PlanNotFound()
        #return roles
        if plan_uuid == 'overcloud':
            return []
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str}, str)
    def validate(self, plan_uuid):
        """Validates a given plan.

        :return: list of validation issues
        :rtype:  list
        """
        LOG.debug('Validating plan: %s' % plan_uuid)

        #try:
        #    issues = tripleo_common.validate_plan(plan_uuid)
        #except SomeException
        #    LOG.exception('Could not validate plan: %s' % plan_uuid)
        #    raise exception.PlanNotFound()
        #return issues
        if plan_uuid == 'overcloud':
            return {}
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose(None, str,
                         status_code=201)
    def deploy(self, plan_uuid):
        """Deploys a given plan.
        """
        print '111111111111111111'
        LOG.debug('Deploys plan: %s' % plan_uuid)
        print plan_uuid
        #try:
        #    tripleo_common.deploy_plan(plan_uuid)
        #except SomeException
        #    LOG.exception('Could not validate plan: %s' % plan_uuid)
        #    raise exception.PlanNotFound()
        if not plan_uuid == 'overcloud':
            raise exception.PlanNotFound()
        print '22222222222222222222222'
