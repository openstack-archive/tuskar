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
#import wsme
from wsme import types as wtypes

from tuskar.api.controllers.v1.types.base import Base
from tuskar.api.controllers.v1.types.capacity import Capacity
from tuskar.api.controllers.v1.types.chassis import Chassis
from tuskar.api.controllers.v1.types.link import Link
from tuskar.api.controllers.v1.types.node import Node
from tuskar.api.controllers.v1.types.relation import Relation


class Rack(Base):
    """A representation of Rack in HTTP body."""

    id = int
    name = wtypes.text
    slots = int
    subnet = wtypes.text
    location = wtypes.text
    state = wtypes.text
    chassis = Chassis
    capacities = [Capacity]
    nodes = [Node]
    links = [Link]
    resource_class = Relation

    @classmethod
    def convert_with_links(self, rack, links):

        kwargs = rack.as_dict()  # returns a new dict, overwriting keys is safe

        if rack.chassis_id:
            kwargs['chassis'] = Chassis(id=rack.chassis_id,
                                        links=[Link.build_ironic_link(
                                            'chassis', rack.chassis_id)])
        else:
            kwargs['chassis'] = Chassis()

        if rack.resource_class_id:
            l = [Link.build('self', pecan.request.host_url, 'resource_classes',
                            rack.resource_class_id)]
            kwargs['resource_class'] = Relation(id=rack.resource_class_id,
                                                links=l)

        kwargs['capacities'] = [Capacity(name=c.name, value=c.value,
                                               unit=c.unit)
                                               for c in rack.capacities]

        kwargs['nodes'] = [Node(id=str(n.id),
                                node_id=n.node_id,
                                links=[
                                    Link.build('self',
                                               pecan.request.host_url,
                                               'nodes', n.id)
                                ])
                           for n in rack.nodes]

        return Rack(links=links, **kwargs)

    @classmethod
    def convert(self, rack, base_url, minimal=False):
        links = [Link.build('self', pecan.request.host_url, 'rack',
                            rack.id)]
        if minimal:
            return Rack(links=links, id=str(rack.id))
