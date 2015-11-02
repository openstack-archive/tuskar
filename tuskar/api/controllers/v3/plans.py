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

    _custom_actions = {'deploy': ['GET'],
                       'parameters': ['GET', 'POST'],
                       'resource_types': ['GET', 'POST'],
                       'roles': ['GET'],
                       'validate': ['GET']}

    # TEMPORARY TEST PLANS
    global test_plan
    global test_parameters
    test_plan = {
        'plan_file_1': 'contents of plan file 1',
        'plan_file_2': 'contents of plan file 2',
        'plan_file_3': 'contents of plan file 3',
    }
    test_parameters = {
        'param1': 'value1',
        'param2': 'value2',
    }
    
    @wsme_pecan.wsexpose([{str: str}])
    def get_all(self):
        """Returns all plans.

        An empty list is returned if no plans are present.

        :return: list of plans; empty list if none are found
        :rtype:  list of dicts
        """
        LOG.debug('Retrieving all plans')
        #return tripleo_common.get_plans
        return [test_plan]

    @wsme_pecan.wsexpose({str: str}, str)
    def get_one(self, plan_name):
        """Returns a specific plan.

        An exception is raised if no plan is found with the
        given name.

        :param plan_name: name of the plan being fetched
        :type  plan_name: str

        :return: matching plan
        :rtype:  dict

        :raises: tuskar.common.exception.PlanNotFound if there
                 is no plan with the given name
        """
        LOG.debug('Retrieving plan: %s' % plan_name)
        #try:
        #    found = tripleo_common.get_plan(plan_name)
        #except SomeException:
        #    LOG.exception('Could not retrieve plan: %s' % plan_name)
        #    raise exception.PlanNotFound()
        #return found
        if plan_name == 'overcloud':
            return test_plan
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose(None, str, status_code=204)
    def delete(self, plan_name):
        """Deletes the given plan.

        :param plan_name: name of the plan being deleted
        :type  plan_name: str

        :raises: tuskar.common.exception.PlanNotFound if there
                 is no plan with the given name
        """

        LOG.debug('Deleting plan: %s' % plan_name)
        #try:
        #    tripleo_common.delete_plan(plan_name)
        #except SomeException:
        #    LOG.exception('Could not delete plan: %s' % plan_name)
        #    raise exception.PlanNotFound()
        if not plan_name == 'overcloud':
            raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str},
                         str,
                         body={str: str},
                         status_code=201)
    def post(self, plan_name, transfer_plan):
        """Creates a new plan.

        :param plan_name: name of the plan
        :type  plan_name: str

        :param transfer_plan: data submitted by the user
        :type  transfer_plan: dict

        :return: created plan
        :rtype:  dict

        :raises: tuskar.common.exception.PlanExists: if a plan
                 with the given name exists
        """
        LOG.debug('Creating plan: %s' % plan_name)
        #try:
            # created = tripleo_common.create_plan(plan_name, transfer_plan)
        #except SomeException
        #    LOG.exception('Plan already exists with this name')
        #    raise exception.PlanExists(plan_name)
        #return created
        if plan_name != 'overcloud':
            raise exception.PlanExists(plan_name)
        return test_plan
    
    @wsme_pecan.wsexpose({str: str},
                         str,
                         body={str: str},
                         status_code=201)
    def patch(self, plan_name, transfer_plan):
        """Patches existing plan.

        :param plan_name: name of the plan being patched
        :type  plan_name: str

        :param transfer_plan: data submitted by the user
        :type  transfer_plan: dict

        :return: patched plan
        :rtype:  dict

        :raises: tuskar.common.exception.PlanNotFound if there
                 is no plan with the given name
        """
        LOG.debug('Updating plan: %s' % transfer_plan)

        #try:
        #    updated = tripleo_common.update_plan(plan_name, plan_files)
        #except SomeException
        #    LOG.exception('Could not patch plan: %s' % plan_name)
        #    raise exception.PlanNotFound()
        #return updated
        if plan_name == 'overcloud':
            return test_plan
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str},
                         str,
                         status_code=201)
    def get_parameters(self, plan_name):
        """Retrieves plan parameters

        :param plan_name: name of the plan
        :type  plan_name: str

        :return: plan parameters
        :rtype:  dict

        :raises: tuskar.common.exception.PlanNotFound if there
                 is no plan with the given name
        """
        LOG.debug('Getting plan parameters: %s' % plan_name)

        #try:
        #    parameters = tripleo_common.get_parameters(plan_name)
        #except SomeException
        #    LOG.exception('Could not find plan parameters: %s' % plan_name)
        #    raise exception.PlanNotFound()
        #return parameters
        if plan_name == 'overcloud':
            return test_parameters
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str},
                         str,
                         body={str: str},
                         status_code=201)
    def post_parameters(self, plan_name, transfer_parameters):
        """Patches existing plan parameters.

        :param plan_name: name of the plan
        :type  plan_name: str

        :param transfer_parameters: data submitted by the user
        :type  transfer_parameters: dict

        :return: plan parameters
        :rtype:  dict
        """
        LOG.debug('Updating plan parameters: %s' % transfer_parameters)

        #try:
        #    params = tripleo_common.update_parameters(plan_name, transfer_parameters)
        #except SomeException
        #    LOG.exception('Could not update plan parameters: %s' % plan_name)
        #    raise exception.PlanNotFound()
        #return params
        if plan_name == 'overcloud':
            return test_parameters
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str},
                         str,
                         status_code=201)
    def get_resource_types(self, plan_name):
        """Retrieves plan resource types.

        :param plan_name: name of the plan
        :type  plan_name: str

        :return: plan resource types
        :rtype:  dict
        """
        LOG.debug('Getting plan resource types: %s' % plan_name)

        #try:
        #    resource_types = tripleo_common.get_resource_types(plan_name)
        #except SomeException
        #    LOG.exception('Could not find plan resource types: %s' % plan_name)
        #    raise exception.PlanNotFound()
        #return resource_types
        if plan_name == 'overcloud':
            return {}
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str},
                         str,
                         body={str: str},
                         status_code=201)
    def post_resource_types(self, plan_name, transfer_resource_types):
        """Patches existing plan resource types.

        :param plan_name: name of the plan
        :type  plan_name: str

        :param transfer_resource_types: data submitted by the user
        :type  transfer_resource_types: dict

        :return: plan resource types
        :rtype:  dict
        """
        LOG.debug('Updating plan resource types: %s' % transfer_resource_types)

        #try:
        #    params = tripleo_common.update_resource_types(plan_name, transfer_resource_types)
        #except SomeException
        #    LOG.exception('Could not update plan resource types: %s' % plan_name)
        #    raise exception.PlanNotFound()
        #return params
        if plan_name == 'overcloud':
            return {}
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose([{str: str}], str)
    def roles(self, plan_name):
        """Returns the roles for a given plan.

        :param plan_name: name of the plan
        :type  plan_name: str

        :return: list of roles
        :rtype:  list
        """
        LOG.debug('Retrieving roles for plan: %s' % plan_name)

        #try:
        #    roles = tripleo_common.get_plan_roles(plan_name)
        #except SomeException
        #    LOG.exception('Could not retrieve roles for plan: %s' %
        #                  plan_name)
        #    raise exception.PlanNotFound()
        #return roles
        if plan_name == 'overcloud':
            return []
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose({str: str}, str)
    def validate(self, plan_name):
        """Validates a given plan.

        :param plan_name: name of the plan
        :type  plan_name: str

        :return: list of validation issues
        :rtype:  list
        """
        LOG.debug('Validating plan: %s' % plan_name)

        #try:
        #    issues = tripleo_common.validate_plan(plan_name)
        #except SomeException
        #    LOG.exception('Could not validate plan: %s' % plan_name)
        #    raise exception.PlanNotFound()
        #return issues
        if plan_name == 'overcloud':
            return {}
        raise exception.PlanNotFound()

    @wsme_pecan.wsexpose(None, str,
                         status_code=201)
    def deploy(self, plan_name):
        """Deploys a given plan.

        :param plan_name: name of the plan
        :type  plan_name: str
        """
        LOG.debug('Deploys plan: %s' % plan_name)
        #try:
        #    tripleo_common.deploy_plan(plan_name)
        #except SomeException
        #    LOG.exception('Could not validate plan: %s' % plan_name)
        #    raise exception.PlanNotFound()
        if not plan_name == 'overcloud':
            raise exception.PlanNotFound()
