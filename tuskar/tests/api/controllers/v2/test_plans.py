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
from tuskar.storage.exceptions import NameAlreadyUsed
from tuskar.tests import base


URL_PLANS = '/v2/plans'


class PlansTests(base.TestCase):

    def setUp(self):
        super(PlansTests, self).setUp()

        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '..', '..', '..', '..', 'api', 'config.py')
        self.app = load_test_app(config_file)

    @mock.patch('tuskar.manager.plan.PlansManager.list_plans')
    def test_get_all(self, mock_list):
        # Setup
        mock_list.return_value = [
            manager_models.DeploymentPlan('a', 'n1', 'd1'),
            manager_models.DeploymentPlan('b', 'n2', 'd2'),
        ]

        # Test
        response = self.app.get(URL_PLANS)
        result = response.json

        # Verify
        mock_list.assert_called_once()
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(2, len(result))
        self.assertEqual(result[0]['name'], 'n1')
        self.assertEqual(result[1]['name'], 'n2')

    @mock.patch('tuskar.manager.plan.PlansManager.list_plans')
    def test_get_all_empty(self, mock_list):
        # Setup
        mock_list.return_value = []

        # Test
        response = self.app.get(URL_PLANS)
        result = response.json

        # Verify
        mock_list.assert_called_once()
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(0, len(result))

    @mock.patch('tuskar.manager.plan.PlansManager.retrieve_plan')
    def test_get_one(self, mock_retrieve):
        # Setup
        p = manager_models.DeploymentPlan('a', 'n', 'd')
        mock_retrieve.return_value = p

        # Test
        url = URL_PLANS + '/' + 'qwerty12345'
        response = self.app.get(url)
        result = response.json

        # Verify
        mock_retrieve.assert_called_once_with('qwerty12345')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(result['name'], 'n')

    @mock.patch('tuskar.manager.plan.PlansManager.retrieve_plan')
    def test_get_one_invalid_uuid(self, mock_retrieve):
        # Setup
        mock_retrieve.side_effect = storage_exceptions.UnknownUUID()

        # Test
        url = URL_PLANS + '/' + 'qwerty12345'
        response = self.app.get(url, status=404)

        # Verify
        mock_retrieve.assert_called_once_with('qwerty12345')
        self.assertEqual(response.status_int, 404)

    @mock.patch('tuskar.manager.plan.PlansManager.retrieve_plan')
    def test_get_one_with_parameters(self, mock_retrieve):
        # Setup
        p = manager_models.DeploymentPlan('a', 'n', 'd')
        p.add_parameters(
            manager_models.PlanParameter(
                name="Param 1", label="1", default=2, hidden=False,
                description="1", value=1, param_type='number', constraints=''),
            manager_models.PlanParameter(
                name="Param 2", label="2", default=['a', ], hidden=False,
                description="2", value=['a', 'b'],
                param_type='comma_delimited_list', constraints=''),
            manager_models.PlanParameter(
                name="Param 3", label="3", default={'a': 2}, hidden=False,
                description="3", value={'a': 1}, param_type='json',
                constraints=''),
        )
        mock_retrieve.return_value = p

        # Test
        url = URL_PLANS + '/' + 'qwerty12345'
        response = self.app.get(url)
        result = response.json

        # Verify
        mock_retrieve.assert_called_once_with('qwerty12345')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(result['name'], 'n')

    @mock.patch('tuskar.manager.plan.PlansManager.delete_plan')
    def test_delete(self, mock_delete):
        # Test
        url = URL_PLANS + '/' + 'qwerty12345'
        response = self.app.delete(url)

        # Verify
        mock_delete.assert_called_once_with('qwerty12345')
        self.assertEqual(response.status_int, 204)

    @mock.patch('tuskar.manager.plan.PlansManager.delete_plan')
    def test_delete_invalid_uuid(self, mock_delete):
        # Setup
        mock_delete.side_effect = storage_exceptions.UnknownUUID()

        # Test
        url = URL_PLANS + '/' + 'qwerty12345'
        response = self.app.delete(url, status=404)

        # Verify
        mock_delete.assert_called_once_with('qwerty12345')
        self.assertEqual(response.status_int, 404)

    @mock.patch('tuskar.manager.plan.PlansManager.create_plan')
    def test_post_no_description(self, mock_create):
        # Setup
        p = manager_models.DeploymentPlan('a', 'n', 'd')
        mock_create.return_value = p

        # Test
        plan_data = {'name': 'new'}
        response = self.app.post_json(URL_PLANS, params=plan_data)
        result = response.json

        # Verify
        mock_create.assert_called_once_with('new', None)
        self.assertEqual(response.status_int, 201)
        self.assertEqual(result['uuid'], p.uuid)
        self.assertEqual(result['name'], p.name)
        self.assertEqual(result['description'], p.description)

    @mock.patch('tuskar.manager.plan.PlansManager.create_plan')
    def test_post(self, mock_create):
        # Setup
        p = manager_models.DeploymentPlan('a', 'n', 'd')
        mock_create.return_value = p

        # Test
        plan_data = {'name': 'new', 'description': 'desc'}
        response = self.app.post_json(URL_PLANS, params=plan_data)
        result = response.json

        # Verify
        mock_create.assert_called_once_with('new', 'desc')
        self.assertEqual(response.status_int, 201)
        self.assertEqual(result['uuid'], p.uuid)
        self.assertEqual(result['name'], p.name)
        self.assertEqual(result['description'], p.description)

    @mock.patch('tuskar.manager.plan.PlansManager.create_plan')
    def test_post_conflict(self, mock_create):
        # Setup
        mock_create.side_effect = NameAlreadyUsed(
            "A master_template with the name 'test.yaml' already exists")

        # Test
        plan_data = {'name': 'new', 'description': 'desc'}
        response = self.app.post_json(URL_PLANS, params=plan_data, status=409)

        # Verify
        mock_create.assert_called_once_with('new', 'desc')
        self.assertEqual(response.status_int, 409)

    @mock.patch('tuskar.manager.plan.PlansManager.package_templates')
    def test_templates(self, mock_package):
        # Setup
        mock_package.return_value = {}

        # Test
        url = URL_PLANS + '/' + 'foo' + '/' + 'templates'
        response = self.app.get(url)
        result = response.body

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertEqual(result, '{}')

    @mock.patch('tuskar.manager.plan.PlansManager.package_templates')
    def test_templates_missing_plan(self, mock_package):
        # Setup
        mock_package.side_effect = storage_exceptions.UnknownUUID()

        # Test
        url = URL_PLANS + '/' + 'foo' + '/' + 'templates'
        response = self.app.get(url, status=404)

        # Verify
        self.assertEqual(response.status_int, 404)

    @mock.patch('tuskar.manager.plan.PlansManager.set_parameter_values')
    def test_patch(self, mock_set):
        # Setup
        p = manager_models.DeploymentPlan('a', 'n', 'd')
        mock_set.return_value = p

        # Test
        values = [{'name': 'foo', 'value': 'bar'}]
        url = URL_PLANS + '/' + 'qwerty12345'
        response = self.app.patch_json(url, values)
        result = response.json

        # Verify
        mock_set.assert_called_once()
        self.assertEqual(mock_set.call_args[0][0], 'qwerty12345')
        self.assertEqual(mock_set.call_args[0][1][0].name, 'foo')
        self.assertEqual(mock_set.call_args[0][1][0].value, 'bar')
        self.assertEqual(response.status_int, 201)
        self.assertEqual(result['name'], p.name)

    @mock.patch('tuskar.manager.plan.PlansManager.set_parameter_values')
    def test_patch_missing_plan(self, mock_set):
        # Setup
        mock_set.side_effect = storage_exceptions.UnknownUUID()

        # Test
        values = [{'name': 'foo', 'value': 'bar'}]
        url = URL_PLANS + '/' + 'qwerty12345'
        response = self.app.patch_json(url, values, status=404)

        # Verify
        self.assertEqual(mock_set.call_args[0][0], 'qwerty12345')
        self.assertEqual(mock_set.call_args[0][1][0].name, 'foo')
        self.assertEqual(mock_set.call_args[0][1][0].value, 'bar')
        self.assertEqual(response.status_int, 404)
