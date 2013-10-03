#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mox

import tuskar.heat.client
from tuskar.tests.api import api


class TestEndpoints(api.FunctionalTest):

    def setUp(self):
        super(TestEndpoints, self).setUp()

    def tearDown(self):
        super(TestEndpoints, self).tearDown()

    def test_it_returns_the_overcloud_endpoints(self):
        heat_outputs = [
            {'output_value': 'http://192.0.2.5:9292/v1/',
             'description': 'URL for the Overcloud Glance service',
             'output_key': 'GlanceURL'},
            {'output_value': 'http://192.0.2.5:8004/v1/',
             'description': 'URL for the Overcloud Heat service',
             'output_key': 'HeatURL'},
            {'output_value': 'http://192.0.2.5:5000/v2.0/',
             'description': 'URL for the Overcloud Keystone service',
             'output_key': 'KeystoneURL'},
            {'output_value': 'http://192.0.2.5:9696',
             'description': 'URL for the Overcloud Neutron service',
             'output_key': 'NeutronURL'},
            {'output_value': 'http://192.0.2.5:8774/v2/',
             'description': 'URL for the Overcloud Nova service',
             'output_key': 'NovaURL'}
         ]

        heat_stack = mox.MockAnything()
        heat_stack.outputs = heat_outputs

        self.mox.StubOutWithMock(tuskar.heat.client.HeatClient, 'get_stack')
        tuskar.heat.client.HeatClient.get_stack().AndReturn(heat_stack)
        self.mox.ReplayAll()

        response = self.app.get('/v1/endpoints')
        self.assertEqual(response.status, '200 OK')
        self.assertRegexpMatches(response.body,
            '"GlanceURL": "http://192.0.2.5:9292/v1/"')
        self.assertRegexpMatches(response.body,
            '"HeatURL": "http://192.0.2.5:8004/v1/"')
        self.assertRegexpMatches(response.body,
            '"KeystoneURL": "http://192.0.2.5:5000/v2.0/"')
        self.assertRegexpMatches(response.body,
            '"NeutronURL": "http://192.0.2.5:9696"')
        self.assertRegexpMatches(response.body,
            '"NovaURL": "http://192.0.2.5:8774/v2/"')
