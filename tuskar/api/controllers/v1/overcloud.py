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
from wsme import api
from wsmeext import pecan as wsme_pecan

import heatclient.exc

from tuskar.api.controllers.v1.types import Error
from tuskar.api.controllers.v1.types import Link
from tuskar.api.controllers.v1.types import Overcloud
import tuskar.heat.client
from tuskar.openstack.common.gettextutils import _


class OvercloudsController(pecan.rest.RestController):
    """Controller for Overcloud."""

    @wsme_pecan.wsexpose(Overcloud, unicode)
    def get_one(self, stack_name):
        heat = tuskar.heat.client.HeatClient()

        try:
            stack = heat.get_stack(stack_name)
        except heatclient.exc.HTTPNotFound as ex:
            response = api.Response(
                None,
                error=Error(faultcode=ex.code, faultstring=str(ex)),
                status_code=ex.code)
            return response

        if not hasattr(stack, 'outputs'):
            faultstring = _('Failed to find Keystone URL.')
            response = api.Response(
                None,
                error=Error(faultcode=404, faultstring=faultstring),
                status_code=404)
            return response

        outputs = stack.outputs
        keystone_param = filter(lambda x: x['output_key'] == 'KeystoneURL',
                                outputs)
        if len(keystone_param) == 0:
            faultstring = _('Failed to find Keystone URL.')
            response = api.Response(
                None,
                error=Error(faultcode=404, faultstring=faultstring),
                status_code=404)
            return response

        keystone_link = Link(rel='keystone',
                             href=keystone_param[0]['output_value'])
        overcloud = Overcloud(stack_name=stack_name,
                              links=[keystone_link])

        return overcloud
