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

from pecan.testing import load_test_app

from tuskar.tests import base


URL_ROLES = '/v2/roles'
URL_PLAN_ROLES = '/v2/plans/plan_uuid/roles'


class RolesTests(base.TestCase):

    def setUp(self):
        super(RolesTests, self).setUp()

        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '..', '..', '..', '..', 'api', 'config.py')
        self.app = load_test_app(config_file)

    def test_get_all(self):
        # Setup

        # Test
        response = self.app.get(URL_ROLES)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(1, len(result))
        self.assertEqual(result[0]['name'], 'foo')

    def test_post(self):
        # Setup
        role_data = {'uuid': 'qwert12345'}

        # Test
        response = self.app.post_json(URL_PLAN_ROLES, params=role_data)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 201)
        self.assertEqual(result['uuid'], '42')
        self.assertEqual(result['name'], 'foo')
        self.assertEqual(result['roles'][0]['uuid'], 'qwert12345')

    def test_delete(self):
        # Setup

        # Test
        response = self.app.delete_json(URL_PLAN_ROLES + '/role_name/role_ver')
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertEqual(result['uuid'], '42')
        self.assertEqual(result['name'], 'foo')
