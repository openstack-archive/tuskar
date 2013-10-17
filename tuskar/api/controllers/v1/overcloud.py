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


class OvercloudsController(pecan.rest.RestController):
    """REST controller for Overcloud."""
    # TODO(ifarkas): add CRUD operations

    _custom_actions = {'entrypoint': ['GET']}

    @pecan.expose('json')
    def entrypoint(self, stack_name):
        heat = tuskar.heat.client.HeatClient()
        # TODO(ifarkas): remove this check when heatclient returns HTTP status
        #                404 instead of 500 in case of a non-existing stack
        #                (https://bugs.launchpad.net/heat/+bug/1239631)
        if not heat.exists_stack():
            pecan.response.status_code = 404
            return {}

        stack = heat.get_stack()
        if not hasattr(stack, 'outputs'):
            pecan.response.status_code = 404
            return {}

        outputs = stack.outputs
        keystone = filter(lambda x: x['output_key'] == 'KeystoneURL', outputs)
        if len(keystone) == 0:
            pecan.response.status_code = 404
            return {}

        return keystone[0]['output_value']
