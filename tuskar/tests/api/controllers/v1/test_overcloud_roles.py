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

from tuskar.db.sqlalchemy import models as db_models
from tuskar.tests import base


URL_ROLES = '/v1/overcloud_roles'


class OvercloudRolesTests(base.TestCase):

    def setUp(self):
        super(OvercloudRolesTests, self).setUp()

        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '..', '..', '..', '..', 'api', 'config.py')
        self.app = load_test_app(config_file)

    @mock.patch('tuskar.db.sqlalchemy.api.Connection.get_overcloud_roles')
    def test_get_all(self, mock_db_get):
        # Setup
        fake_results = [db_models.OvercloudRole(name='foo')]
        mock_db_get.return_value = fake_results

        # Test
        response = self.app.get(URL_ROLES)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(1, len(result))
        self.assertEqual(result[0]['name'], 'foo')

        mock_db_get.assert_called_once()

    @mock.patch('tuskar.db.sqlalchemy.api.'
                'Connection.get_overcloud_role_by_id')
    def test_get_one(self, mock_db_get):
        # Setup
        fake_result = db_models.OvercloudRole(name='foo')
        mock_db_get.return_value = fake_result

        # Test
        url = URL_ROLES + '/' + '12345'
        response = self.app.get(url)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertEqual(result['name'], 'foo')

        mock_db_get.assert_called_once_with(12345)

    @mock.patch('tuskar.db.sqlalchemy.api.Connection.create_overcloud_role')
    def test_post(self, mock_db_create):
        # Setup
        create_me = {'name': 'new'}

        fake_created = db_models.OvercloudRole(name='created')
        mock_db_create.return_value = fake_created

        # Test
        response = self.app.post_json(URL_ROLES, params=create_me)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 201)
        self.assertEqual(result['name'], fake_created.name)

        self.assertEqual(1, mock_db_create.call_count)
        db_create_model = mock_db_create.call_args[0][0]
        self.assertTrue(isinstance(db_create_model,
                                   db_models.OvercloudRole))
        self.assertEqual(db_create_model.name, create_me['name'])

    @mock.patch('tuskar.db.sqlalchemy.api.Connection.update_overcloud_role')
    def test_put(self, mock_db_update):
        # Setup
        changes = {'name': 'updated'}

        fake_updated = db_models.OvercloudRole(name='after-update')
        mock_db_update.return_value = fake_updated

        # Test
        url = URL_ROLES + '/' + '12345'
        response = self.app.put_json(url, params=changes)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertEqual(result['name'], fake_updated.name)

        self.assertEqual(1, mock_db_update.call_count)
        db_update_model = mock_db_update.call_args[0][0]
        self.assertTrue(isinstance(db_update_model,
                                   db_models.OvercloudRole))
        self.assertEqual(db_update_model.id, 12345)
        self.assertEqual(db_update_model.name, changes['name'])

    @mock.patch('tuskar.db.sqlalchemy.api.'
                'Connection.delete_overcloud_role_by_id')
    def test_delete(self, mock_db_delete):
        # Test
        url = URL_ROLES + '/' + '12345'
        response = self.app.delete(url)

        # Verify
        self.assertEqual(response.status_int, 204)

        mock_db_delete.assert_called_once_with(12345)
