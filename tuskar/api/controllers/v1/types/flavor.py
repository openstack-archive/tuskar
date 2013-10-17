# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
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
import wsme
from wsme import types as wtypes

from tuskar.api.controllers.v1.types.base import Base
from tuskar.api.controllers.v1.types.capacity import Capacity
from tuskar.api.controllers.v1.types.link import Link


class Flavor(Base):
    """A representation of Flavor in HTTP body."""
    #FIXME - I want id to be UUID - String
    id = wsme.wsattr(int, mandatory=False)
    name = wsme.wsattr(wtypes.text, mandatory=False)
    max_vms = wsme.wsattr(int, mandatory=False)
    capacities = [Capacity]
    links = [Link]

    @classmethod
    def add_capacities(self, rc_id, flavor):
        capacities = []
        for c in flavor.capacities:
            capacities.append(Capacity(name=c.name,
                                       value=c.value,
                                       unit=c.unit))

        links = [Link.build('self', pecan.request.host_url,
                            "resource_classes/%s/flavors" % rc_id, flavor.id
                            )]

        return Flavor(capacities=capacities, links=links, **(flavor.as_dict()))
