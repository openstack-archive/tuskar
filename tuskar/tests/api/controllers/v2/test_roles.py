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

import os

import mock
from pecan.testing import load_test_app

from tuskar.manager import models as manager_models
from tuskar.storage import exceptions as storage_exceptions
from tuskar.tests import base


URL_ROLES = '/v2/roles'
URL_PLAN_ROLES = '/v2/plans/plan_uuid/roles'


class RolesTests(base.TestCase):

    def setUp(self):
        super(RolesTests, self).setUp()

        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '..', '..', '..', '..', 'api', 'config.py')
        self.app = load_test_app(config_file)

    @mock.patch('tuskar.manager.role.RoleManager.list_roles')
    def test_get_all(self, mock_list):
        # Setup
        mock_list.return_value = [
            manager_models.Role('a', 'n1', 1, 'd1', 't1'),
            manager_models.Role('b', 'n2', 2, 'd2', 't2'),
        ]

        # Test
        response = self.app.get(URL_ROLES)
        result = response.json

        # Verify
        mock_list.assert_called_once_with(only_latest=False)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(2, len(result))
        self.assertEqual(result[0]['uuid'], 'a')
        self.assertEqual(result[0]['name'], 'n1')
        self.assertEqual(result[0]['description'], 'd1')
        self.assertEqual(result[1]['uuid'], 'b')
        self.assertEqual(result[1]['name'], 'n2')
        self.assertEqual(result[1]['description'], 'd2')

    @mock.patch('tuskar.manager.plan.PlansManager.add_role_to_plan')
    def test_post(self, mock_add):
        # Setup
        p = manager_models.DeploymentPlan('a', 'n', 'd')
        mock_add.return_value = p

        # Test
        role_data = {'uuid': 'qwerty12345'}
        response = self.app.post_json(URL_PLAN_ROLES, params=role_data)
        result = response.json

        # Verify
        mock_add.assert_called_once_with('plan_uuid', 'qwerty12345')
        self.assertEqual(response.status_int, 201)
        self.assertEqual(result['uuid'], 'a')
        self.assertEqual(result['name'], 'n')

    @mock.patch('tuskar.manager.plan.PlansManager.add_role_to_plan')
    def test_post_duplicate(self, mock_add):
        # Setup
        mock_add.side_effect = ValueError()

        # Test
        role_data = {'uuid': 'qwerty12345'}
        response = self.app.post_json(URL_PLAN_ROLES, params=role_data,
                                      status=409)

        # Verify
        mock_add.assert_called_once_with('plan_uuid', 'qwerty12345')
        self.assertEqual(response.status_int, 409)

    @mock.patch('tuskar.manager.plan.PlansManager.add_role_to_plan')
    def test_post_unkown_uuid(self, mock_add):
        # Setup
        mock_add.side_effect = storage_exceptions.UnknownUUID()

        # Test
        role_data = {'uuid': 'qwerty12345'}
        response = self.app.post_json(URL_PLAN_ROLES, params=role_data,
                                      status=404)

        # Verify
        mock_add.assert_called_once_with('plan_uuid', 'qwerty12345')
        self.assertEqual(response.status_int, 404)

    @mock.patch('tuskar.manager.plan.PlansManager.remove_role_from_plan')
    def test_delete(self, mock_remove):
        # Setup
        p = manager_models.DeploymentPlan('a', 'n', 'd')
        mock_remove.return_value = p

        # Test
        response = self.app.delete_json(URL_PLAN_ROLES + '/role_uuid')
        result = response.json

        # Verify
        mock_remove.assert_called_once_with('plan_uuid', 'role_uuid')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(result['uuid'], 'a')
        self.assertEqual(result['name'], 'n')

    @mock.patch('tuskar.manager.plan.PlansManager.remove_role_from_plan')
    def test_delete_unkown_uuid(self, mock_remove):
        # Setup
        mock_remove.side_effect = storage_exceptions.UnknownUUID()

        # Test
        response = self.app.delete_json(URL_PLAN_ROLES + '/qwerty12345',
                                        status=404)

        # Verify
        mock_remove.assert_called_once_with('plan_uuid', 'qwerty12345')
        self.assertEqual(response.status_int, 404)
