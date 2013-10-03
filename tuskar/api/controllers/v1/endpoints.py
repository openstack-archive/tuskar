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

import pecan

import tuskar.heat.client


class EndpointsController(pecan.rest.RestController):
    """Controller for the overcloud API endpoints
    """

    @pecan.expose('json')
    def get_all(self):
        heat = tuskar.heat.client.HeatClient()
        # TODO(ifarkas): remove this check when heatclient returns HTTP status
        #                404 instead of 500 in case of a non-existing stack
        if not heat.exists_stack():
            pecan.response.status_code = 404
            return dict()

        stack = heat.get_stack()
        if not hasattr(stack, 'outputs'):
            return dict()

        outputs = stack.outputs
        endpoints = dict()
        for service in outputs:
            endpoints[service['output_key']] = service['output_value']

        return endpoints
