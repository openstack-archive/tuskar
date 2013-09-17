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
from wsme import types as wtypes

from tuskar.api.controllers.v1.types.base import Base
from tuskar.api.controllers.v1.types.link import Link
from tuskar.api.controllers.v1.types.relation import Relation


class Node(Base):
    """A Node representation."""

    id = wtypes.text
    # FIXME: We expose this as nova_baremetal_node_id, but are not yet changing
    # the column name in the database, because this is a more involved change.
    nova_baremetal_node_id = wtypes.text
    rack = Relation
    links = [Link]

    @classmethod
    def convert(self, node):
        kwargs = node.as_dict()
        links = [Link.build('self', pecan.request.host_url, 'nodes',
                            node.id)]
        rack_link = [Link.build('self', pecan.request.host_url,
                                'racks', node.rack_id)]
        kwargs['rack'] = Relation(id=node.rack_id, links=rack_link)
        kwargs['id'] = str(node.id)
        kwargs['nova_baremetal_node_id'] = str(node.node_id)
        return Node(links=links, **kwargs)
