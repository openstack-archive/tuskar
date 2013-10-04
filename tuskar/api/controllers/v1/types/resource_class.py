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
from tuskar.api.controllers.v1.types.flavor import Flavor
from tuskar.api.controllers.v1.types.link import Link
from tuskar.api.controllers.v1.types.relation import Relation


class ResourceClass(Base):
    """A representation of Resource Class in HTTP body."""

    id = int
    name = wtypes.text
    service_type = wtypes.text
    image_id = wtypes.wsattr(wtypes.text, mandatory=False, default=None)
    racks = [Relation]
    flavors = [Flavor]
    links = [Link]

    @classmethod
    def convert(self, resource_class, base_url, minimal=False):
        links = [Link.build('self', pecan.request.host_url, 'resource_classes',
                            resource_class.id)]
        if minimal:
            return ResourceClass(links=links, id=str(resource_class.id))
        else:
            racks = []
            if resource_class.racks:
                for r in resource_class.racks:
                    l = [Link.build('self', pecan.request.host_url,
                                    'racks', r.id)]
                    rack = Relation(id=r.id, links=l)
                    racks.append(rack)

            flavors = []
            if resource_class.flavors:
                for flav in resource_class.flavors:

                    flavor = Flavor.add_capacities(resource_class.id, flav)
                    flavors.append(flavor)
            return ResourceClass(links=links, racks=racks, flavors=flavors,
                                 **(resource_class.as_dict()))
