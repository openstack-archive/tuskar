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

import heatclient.exc
import heatclient.v1.stacks

import tuskar.heat.client
from tuskar.tests.api import api


class TestOverclouds(api.FunctionalTest):

    def test_it_returns_the_overcloud_endpoints(self):
        heat_outputs = [
            {'output_value': 'http://192.0.2.5:5000/v2.0/',
             'description': 'URL for the Overcloud Keystone service',
             'output_key': 'KeystoneURL'},
         ]

        heat_stack = mox.MockAnything()
        heat_stack.outputs = heat_outputs

        self.mox.StubOutWithMock(tuskar.heat.client.HeatClient, 'get_stack')
        tuskar.heat.client.HeatClient.get_stack('stack_name').AndReturn(
            heat_stack)
        self.mox.ReplayAll()

        response = self.app.get('/v1/overclouds/stack_name')
        self.assertEqual(response.status, '200 OK')
        self.assertRegexpMatches(response.body, 'http://192.0.2.5:5000/v2.0/')

    def test_it_returns_404_for_nonexisting_overcloud(self):
        self.mox.StubOutWithMock(tuskar.heat.client.HeatClient, 'get_stack')
        tuskar.heat.client.HeatClient.get_stack(
            'stack_name').AndRaise(heatclient.exc.HTTPNotFound())
        self.mox.ReplayAll()

        response = self.app.get('/v1/overclouds/stack_name',
                                expect_errors=True)
        self.assertEqual(response.status, '404 Not Found')

    def test_it_returns_404_during_provisioning(self):
        heat_stack = self.mox.CreateMock(heatclient.v1.stacks.Stack)
        self.mox.StubOutWithMock(tuskar.heat.client.HeatClient, 'get_stack')
        tuskar.heat.client.HeatClient.get_stack('stack_name').AndReturn(
            heat_stack)
        self.mox.ReplayAll()

        response = self.app.get('/v1/overclouds/stack_name',
                                expect_errors=True)
        self.assertEqual(response.status, '404 Not Found')
