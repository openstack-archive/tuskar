# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
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

"""
Version 1 of the Tuskar API
"""

import pecan
from pecan import rest
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan
from oslo.config import cfg

from tuskar.openstack.common import log

LOG = log.getLogger(__name__)
CONF = cfg.CONF

ironic_opts = [
        cfg.StrOpt('ironic_url',
            default='http://ironic.local:6543/v1',
            help='Ironic API entrypoint URL'),
        ]

CONF.register_opts(ironic_opts)

def _make_link(rel_name, url, type, type_arg):
    return Link(href=('%s/v1/%s/%s') % (url, type, type_arg),
                rel=rel_name)

def _ironic_link(rel_name, resource_id):
    return Link(href=('%s/%s') % (CONF.ironic_url, resource_id), rel=rel_name)


class Base(wtypes.Base):

    def __init__(self, **kwargs):
        self.fields = list(kwargs)
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @classmethod
    def from_db_model(cls, m):
        return cls(**m.as_dict())

    @classmethod
    def from_db_and_links(cls, m, links):
        return cls(links=links, **(m.as_dict()))

    def as_dict(self):
        return dict((k, getattr(self, k))
                for k in self.fields
                if hasattr(self, k) and
                getattr(self, k) != wsme.Unset)

    def get_id(self):
        """Returns the ID of this resource as specified in the self link"""

        # FIXME(mtaylor) We should use a more robust method for parsing the URL
        return self.links[0].href.split("/")[-1]

class Link(Base):
    """A link representation"""

    href = wtypes.text
    "The url of a link"

    rel = wtypes.text
    "The name of a link"


class Chassis(Base):
    """A chassis representation"""

    id    = wtypes.text
    links = [Link]


class Capacity(Base):
    """A capacity representation"""

    name = wtypes.text
    value = wtypes.text

class Node(Base):
    """A Node representation"""

    id    = wtypes.text
    links = [Link]


class Rack(Base):
    """A representation of Rack in HTTP body"""

    id = int
    name = wtypes.text
    slots = int
    subnet = wtypes.text
    chassis = Chassis
    capacities = [Capacity]
    nodes = [Node]
    links = [Link]

    @classmethod
    def convert_with_links(self, rack, links):

        if rack.chassis_id:
            chassis = Chassis(id=rack.chassis_id, links=[_ironic_link('chassis', rack.chassis_id)])
        else:
            chassis = Chassis()

        capacities = [Capacity(name=c.name, value=c.value) for c in rack.capacities]

        nodes = [Node(id=n.node_id, links=[_ironic_link('node', n.node_id)]) for n in rack.nodes]

        return Rack(links=links, chassis=chassis, capacities=capacities,
                nodes=nodes, **(rack.as_dict()))

    @classmethod
    def convert(self, rack, base_url, minimal=False):
        links = [_make_link('self', pecan.request.host_url, 'rack',
                             rack.id)]
        if minimal:
            return Rack(links=links, id=str(rack.id))

class ResourceClass(Base):
    """A representation of Resource Class in HTTP body"""

    id = int
    name = wtypes.text
    service_type = wtypes.text
    racks = [Rack]
    links = [Link]

    @classmethod
    def convert(self, resource_class, base_url, minimal=False):
        links = [_make_link('self', pecan.request.host_url, 'resource_classes',
                             resource_class.id)]
        if minimal:
            return ResourceClass(links=links, id=str(resource_class.id))
        else:
            racks = []
            if resource_class.racks:
                for r in resource_class.racks:
                    rack = Rack.convert(r, base_url, True)
                    racks.append(rack)
            return ResourceClass(links=links, racks=racks,
                                 **(resource_class.as_dict()))

class RacksController(rest.RestController):
    """REST controller for Rack"""

    @wsme.validate(Rack)
    @wsme_pecan.wsexpose(Rack, body=Rack, status_code=201)
    def post(self, rack):
        """Create a new Rack."""
        try:
            result = pecan.request.dbapi.create_rack(rack)
            links = [_make_link('self', pecan.request.host_url, 'racks',
                    result.id)]
        except Exception as e:
            LOG.exception(e)
            raise wsme.exc.ClientSideError(_("Invalid data"))

        # 201 Created require Location header pointing to newly created
        #     resource
        #
        # FIXME(mfojtik): For some reason, Pecan does not return 201 here
        #                 as configured above
        #
        pecan.response.headers['Location'] = str(links[0].href)
        pecan.response.status_code = 201
        return Rack.convert_with_links(result, links)

    @wsme_pecan.wsexpose([Rack])
    def get_all(self):
        """Retrieve a list of all racks"""
        result = []
        links = []
        for rack in pecan.request.dbapi.get_racks(None):
            links = [_make_link('self', pecan.request.host_url, 'racks',
                    rack.id)]
            result.append(Rack.convert_with_links(rack, links))
        return result

    @wsme_pecan.wsexpose(Rack, unicode)
    def get_one(self, rack_id):
        """Retrieve information about the given Rack."""
        rack = pecan.request.dbapi.get_rack(rack_id)
        links = [_make_link('self', pecan.request.host_url, 'racks',
                rack.id)]
        return Rack.convert_with_links(rack, links)

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, rack_id):
        """Remove the Rack"""

        # FIXME(mfojtik: For some reason, Pecan does not return 201 here
        #                as configured above
        #
        pecan.response.status_code = 204
        pecan.request.dbapi.delete_rack(rack_id)

class ResourceClassesController(rest.RestController):
    """REST controller for Resource Class"""

    @wsme.validate(ResourceClass)
    @wsme_pecan.wsexpose(ResourceClass, body=ResourceClass, status_code=201)
    def post(self, resource_class):
        """Create a new Resource Class."""
        try:
            result = pecan.request.dbapi.create_resource_class(resource_class)
        except Exception as e:
            LOG.exception(e)
            raise wsme.exc.ClientSideError(_("Invalid data"))

        # 201 Created require Location header pointing to newly created
        #     resource
        #
        # FIXME(mfojtik): For some reason, Pecan does not return 201 here
        #                 as configured above
        #
        rc = ResourceClass.convert(result, pecan.request.host_url)
        pecan.response.headers['Location'] = str(rc.links[0].href)
        pecan.response.status_code = 201
        return rc


    @wsme_pecan.wsexpose([ResourceClass])
    def get_all(self):
        """Retrieve a list of all Resource Classes"""
        result = []
        for rc in pecan.request.dbapi.get_resource_classes(None):
            result.append(ResourceClass.convert(rc, pecan.request.host_url))
        return result


    @wsme_pecan.wsexpose(ResourceClass, unicode)
    def get_one(self, resource_class_id):
        """Retrieve information about the given Resource Class."""
        resource_class = pecan.request.dbapi.get_resource_class(resource_class_id)
        links = [_make_link('self', pecan.request.host_url, 'resource_classes',
                resource_class.id)]
        return ResourceClass.convert(resource_class, pecan.request.host_url)


    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, resource_class_id):
        """Remove the Resource Class"""
        pecan.request.dbapi.delete_resource_class(resource_class_id)

class Controller(object):
    """Version 1 API controller root."""

    racks = RacksController()

    resource_classes = ResourceClassesController()
