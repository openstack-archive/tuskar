# -*- encoding: utf-8 -*-
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

import mock
import os

from pecan.testing import load_test_app

from tuskar.api.controllers.v1 import overcloud
from tuskar.common import exception
from tuskar.db.sqlalchemy import models as db_models
from tuskar.tests import base


URL_OVERCLOUDS = '/v1/overclouds'


class OvercloudTests(base.TestCase):

    def setUp(self):
        super(OvercloudTests, self).setUp()

        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '..', '..', '..', '..', 'api', 'config.py')
        self.app = load_test_app(config_file)

    @mock.patch('tuskar.db.sqlalchemy.api.Connection.get_overclouds')
    def test_get_all(self, mock_db_get):
        # Setup
        fake_results = [db_models.Overcloud(name='foo')]
        mock_db_get.return_value = fake_results

        # Test
        response = self.app.get(URL_OVERCLOUDS)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(1, len(result))
        self.assertEqual(result[0]['name'], 'foo')

        mock_db_get.assert_called_once()

    @mock.patch('tuskar.db.sqlalchemy.api.'
                'Connection.get_overcloud_by_id')
    def test_get_one(self, mock_db_get):
        # Setup
        fake_result = db_models.Overcloud(name='foo')
        mock_db_get.return_value = fake_result

        # Test
        url = URL_OVERCLOUDS + '/' + '12345'
        response = self.app.get(url)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertEqual(result['name'], 'foo')

        mock_db_get.assert_called_once_with(12345)

    def test_parse_counts(self):
        # Setup
        overcloud_role_1 = db_models.OvercloudRole(
            image_name='overcloud-compute')

        overcloud_role_2 = db_models.OvercloudRole(
            image_name='overcloud-block-storage')

        overcloud_role_count_1 = db_models.OvercloudRoleCount(
            overcloud_role_id=2, num_nodes=5, overcloud_role=overcloud_role_1)

        overcloud_role_count_2 = db_models.OvercloudRoleCount(
            overcloud_role_id=2, num_nodes=9, overcloud_role=overcloud_role_2)

        mock_counts = [overcloud_role_count_1, overcloud_role_count_2]

        # Test
        result = overcloud.parse_counts(mock_counts)

        # Verify
        self.assertEqual(result, {'overcloud-compute': 5,
                                  'overcloud-block-storage': 9})

    def test_filter_template_attributes(self):
        # Setup
        allowed_data = {'Parameters': {
            'Allowed_1': 42,
            'Allowed_2': 21,
        }}

        attributes = {
            'NotAllowed_1': "Infinity",
            'Allowed_1': 42,
            'NotAllowed_2': "SubZero",
            'Allowed_2': 21,
            'NotAllowed_3': "Goro",
        }

        # Test
        result = overcloud.filter_template_attributes(allowed_data, attributes)

        # Verify
        self.assertEqual(result, {'Allowed_1': 42,
                                  'Allowed_2': 21})

    @mock.patch('tuskar.heat.template_tools.merge_templates')
    @mock.patch(
        'tuskar.heat.client.HeatClient.__new__', return_value=mock.Mock(**{
            'validate_template.return_value': (True, {}),
            'exists_stack.return_value': False,
            'create_stack.return_value': True,
        })
    )
    def test_create_stack(self, mock_heat_client, mock_heat_merge_templates):
        # Setup
        mock_heat_merge_templates.return_value = None

        # Test
        response = overcloud.process_stack({}, {}, create=True)

        # Verify
        self.assertEqual(response, None)

    @mock.patch('tuskar.heat.template_tools.merge_templates')
    @mock.patch(
        'tuskar.heat.client.HeatClient.__new__', return_value=mock.Mock(**{
            'validate_template.return_value': (True, {}),
            'exists_stack.return_value': False,
            'create_stack.return_value': False,
        })
    )
    def test_create_stack_heat_exception(self, mock_heat_client,
                                         mock_heat_merge_templates):
        # Setup
        mock_heat_merge_templates.return_value = None

        # Test and Verify
        self.assertRaises(
            exception.HeatTemplateCreateFailed,
            overcloud.process_stack, {}, {}, True)

    @mock.patch('tuskar.heat.template_tools.merge_templates')
    @mock.patch(
        'tuskar.heat.client.HeatClient.__new__', return_value=mock.Mock(**{
            'validate_template.return_value': (True, {}),
            'exists_stack.return_value': True,
            'create_stack.return_value': True,
        })
    )
    def test_create_stack_existing_exception(self, mock_heat_client,
                                             mock_heat_merge_templates):
        # Setup
        mock_heat_merge_templates.return_value = None

        # Test and Verify
        self.assertRaises(
            exception.StackAlreadyCreated, overcloud.process_stack, {}, {},
            True)

    @mock.patch('tuskar.heat.template_tools.merge_templates')
    @mock.patch(
        'tuskar.heat.client.HeatClient.__new__', return_value=mock.Mock(**{
            'validate_template.return_value': (False, {}),
            'exists_stack.return_value': False,
            'create_stack.return_value': True,
        })
    )
    def test_create_stack_not_valid_exception(self, mock_heat_client,
                                              mock_heat_merge_templates):
        # Setup
        mock_heat_merge_templates.return_value = None

        # Test and Verify
        self.assertRaises(
            exception.InvalidHeatTemplate, overcloud.process_stack, {}, {},
            True)

    @mock.patch('tuskar.api.controllers.v1.overcloud.process_stack')
    @mock.patch('tuskar.db.sqlalchemy.api.Connection.create_overcloud')
    def test_post(self, mock_db_create, mock_process_stack):
        # Setup
        create_me = {'name': 'new'}

        fake_created = db_models.Overcloud(name='created')
        mock_db_create.return_value = fake_created
        mock_process_stack.return_value = None

        # Test
        response = self.app.post_json(URL_OVERCLOUDS, params=create_me)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 201)
        self.assertEqual(result['name'], fake_created.name)

        self.assertEqual(1, mock_db_create.call_count)
        db_create_model = mock_db_create.call_args[0][0]
        self.assertTrue(isinstance(db_create_model,
                                   db_models.Overcloud))
        self.assertEqual(db_create_model.name, create_me['name'])

    @mock.patch('tuskar.heat.template_tools.merge_templates')
    @mock.patch(
        'tuskar.heat.client.HeatClient.__new__', return_value=mock.Mock(**{
            'validate_template.return_value': (True, {}),
            'exists_stack.return_value': True,
            'create_stack.return_value': True,
        })
    )
    def test_update_stack(self, mock_heat_client, mock_heat_merge_templates):
        # Setup
        mock_heat_merge_templates.return_value = None

        # Test
        response = overcloud.process_stack({}, {})

        # Verify
        self.assertEqual(response, None)

    @mock.patch('tuskar.heat.template_tools.merge_templates')
    @mock.patch(
        'tuskar.heat.client.HeatClient.__new__', return_value=mock.Mock(**{
            'validate_template.return_value': (True, {}),
            'exists_stack.return_value': True,
            'update_stack.return_value': False,
        })
    )
    def test_update_stack_heat_exception(self, mock_heat_client,
                                         mock_heat_merge_templates):
        # Setup
        mock_heat_merge_templates.return_value = None

        # Test and Verify
        self.assertRaises(
            exception.HeatTemplateUpdateFailed, overcloud.process_stack, {},
            {})

    @mock.patch('tuskar.heat.template_tools.merge_templates')
    @mock.patch(
        'tuskar.heat.client.HeatClient.__new__', return_value=mock.Mock(**{
            'validate_template.return_value': (True, {}),
            'exists_stack.return_value': False,
            'create_stack.return_value': True,
        })
    )
    def test_update_stack_not_existing_exception(self, mock_heat_client,
                                                 mock_heat_merge_templates):
        # Setup
        mock_heat_merge_templates.return_value = None

        # Test and Verify
        self.assertRaises(
            exception.StackNotFound, overcloud.process_stack, {}, {})

    @mock.patch('tuskar.heat.template_tools.merge_templates')
    @mock.patch(
        'tuskar.heat.client.HeatClient.__new__', return_value=mock.Mock(**{
            'validate_template.return_value': (False, {}),
            'exists_stack.return_value': True,
            'create_stack.return_value': True,
        })
    )
    def test_update_stack_not_valid_exception(self, mock_heat_client,
                                              mock_heat_merge_templates):
        # Setup
        mock_heat_merge_templates.return_value = None

        # Test and Verify
        self.assertRaises(
            exception.InvalidHeatTemplate, overcloud.process_stack, {}, {})

    @mock.patch('tuskar.api.controllers.v1.overcloud.process_stack')
    @mock.patch('tuskar.db.sqlalchemy.api.Connection.update_overcloud')
    def test_put(self, mock_db_update, mock_process_stack):
        # Setup
        changes = {'name': 'updated'}

        fake_updated = db_models.Overcloud(name='after-update',
                                           attributes=[],
                                           counts=[])
        mock_db_update.return_value = fake_updated
        mock_process_stack.return_value = None

        # Test
        url = URL_OVERCLOUDS + '/' + '12345'
        response = self.app.put_json(url, params=changes)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertEqual(result['name'], fake_updated.name)

        self.assertEqual(1, mock_db_update.call_count)
        db_update_model = mock_db_update.call_args[0][0]
        self.assertTrue(isinstance(db_update_model,
                                   db_models.Overcloud))
        self.assertEqual(db_update_model.id, 12345)
        self.assertEqual(db_update_model.name, changes['name'])

    @mock.patch('tuskar.db.sqlalchemy.api.'
                'Connection.delete_overcloud_by_id')
    @mock.patch(
        'tuskar.heat.client.HeatClient.__new__', return_value=mock.Mock(**{
            'delete_stack.return_value': True,
        })
    )
    def test_delete(self, mock_heat_client, mock_db_delete):
        # Test
        url = URL_OVERCLOUDS + '/' + '12345'
        response = self.app.delete(url)

        # Verify
        self.assertEqual(response.status_int, 204)

        mock_db_delete.assert_called_once_with(12345)
