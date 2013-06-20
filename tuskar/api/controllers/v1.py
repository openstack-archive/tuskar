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

from tuskar.openstack.common import log

LOG = log.getLogger(__name__)


def _make_link(rel_name, url, type, type_arg):
    return Link(href=('%s/v1/%s/%s') % (url, type, type_arg),
                rel=rel_name)


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


class Link(Base):
    """A link representation"""

    href = wtypes.text
    "The url of a link"

    rel = wtypes.text
    "The name of a link"


class Rack(Base):
    """A representation of Rack in HTTP body"""

    id = int
    name = wtypes.text
    slots = int
    subnet = wtypes.text
    chassis = wtypes.DictType(wtypes.text, [wtypes.DictType(wtypes.text,
        wtypes.text)])
    capacities = [wtypes.DictType(wtypes.text, wtypes.text)]
    links = [Link]

class ResourceClass(Base):
    """A representation of Resource Class in HTTP body"""

    id = int
    name = wtypes.text
    service_type = wtypes.text

class RacksController(rest.RestController):
    """REST controller for Rack"""

    @wsme.validate(Rack)
    @wsme_pecan.wsexpose(Rack, body=Rack, status_code=201)
    def post(self, rack):
        """Create a new Rack."""
        try:
            new_rack = Rack(
                    name=rack.name,
                    slots=rack.slots,
                    subnet=rack.subnet,
                    capacities=rack.capacities,
                    chassis_url=rack.chassis['links'][0]['href'],
                    )
            d = new_rack.as_dict()
            result = pecan.request.dbapi.create_rack(d)
            link = _make_link('self', pecan.request.host_url, 'racks',
                    result.id)
        except Exception as e:
            LOG.exception(e)
            raise wsme.exc.ClientSideError(_("Invalid data"))
        pecan.response.headers['Location'] = str(link.href)
        pecan.response.status_code = 201
        return Rack.from_db_and_links(result, [link])

    @wsme_pecan.wsexpose([Rack])
    def get_all(self):
        """Retrieve a list of all racks"""
        result = []
        links = []
        for rack in pecan.request.dbapi.get_racks(None):
            links = [_make_link('self', pecan.request.host_url, 'racks',
                    rack.id)]
            result.append(Rack.from_db_and_links(rack, links))

        return result

    @wsme_pecan.wsexpose(Rack, unicode)
    def get_one(self, rack_id):
        """Retrieve information about the given Rack."""
        rack = pecan.request.dbapi.get_rack(rack_id)
        link = _make_link('self', pecan.request.host_url, 'racks',
                rack.id)
        return Rack.from_db_and_links(rack, [link])

class ResourceClassesController(rest.RestController):
    """REST controller for Resource Class"""

    @wsme.validate(ResourceClass)
    @wsme_pecan.wsexpose(ResourceClass, body=ResourceClass, status_code=201)
    def post(self, resource_class):
        """Create a new Resource Class."""
        try:
            rc = ResourceClass(name=resource_class.name,
                               service_type=resource_class.service_type)
            result = pecan.request.dbapi.create_resource_class(rc.as_dict())
        except Exception as e:
            LOG.exception(e)
            raise wsme.exc.ClientSideError(_("Invalid data"))
        return ResourceClass.from_db_model(result)

    @wsme_pecan.wsexpose([ResourceClass])
    def get_all(self):
        """Retrieve a list of all resource classes"""
        result = pecan.request.dbapi.get_resource_classes(None)
        return [ResourceClass.from_db_model(resource_class) for resource_class in result]

class Controller(object):
    """Version 1 API controller root."""

    racks = RacksController()

    resource_classes = ResourceClassesController()
