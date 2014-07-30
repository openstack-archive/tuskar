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


URL_PLANS = '/v2/plans'


class PlansTests(base.TestCase):

    def setUp(self):
        super(PlansTests, self).setUp()

        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '..', '..', '..', '..', 'api', 'config.py')
        self.app = load_test_app(config_file)

    def test_get_all(self):
        # Setup

        # Test
        response = self.app.get(URL_PLANS)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(1, len(result))
        self.assertEqual(result[0]['name'], 'foo')

    def test_get_one(self):
        # Setup

        # Test
        url = URL_PLANS + '/' + 'qwerty12345'
        response = self.app.get(url)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertEqual(result['name'], 'foo')

    def test_delete(self):
        # Test
        url = URL_PLANS + '/' + 'qwerty12345'
        response = self.app.delete(url)

        # Verify
        self.assertEqual(response.status_int, 204)

    def test_post(self):
        # Setup
        plan_data = {'name': 'new'}

        # Test
        response = self.app.post_json(URL_PLANS, params=plan_data)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 201)
        self.assertEqual(result['name'], plan_data['name'])

    def test_templates(self):
        # Setup

        # Test
        url = URL_PLANS + '/' + 'foo' + '/' + 'templates'
        response = self.app.get(url)
        result = response.body

        # Verify
        self.assertEqual(response.status_int, 200)
        self.assertEqual(result, 'foo')

    def test_patch(self):
        # Setup
        plan_data = {'name': 'new'}

        # Test
        url = URL_PLANS + '/' + 'qwert12345'
        response = self.app.patch_json(url, plan_data)
        result = response.json

        # Verify
        self.assertEqual(response.status_int, 201)
        self.assertEqual(result['name'], plan_data['name'])
