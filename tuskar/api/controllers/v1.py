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


class Base(wtypes.Base):

    def __init__(self, **kwargs):
        self.fields = list(kwargs)
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @classmethod
    def from_db_model(cls, m):
        return cls(**m.as_dict())

    def as_dict(self):
        return dict((k, getattr(self, k))
                for k in self.fields
                if hasattr(self, k) and
                getattr(self, k) != wsme.Unset)


class Sausage(Base):
    """A representation of a sausage."""

    blaa_id = int
    name = wtypes.text

    @classmethod
    def sample(cls):
        return cls(blaa_id=1, name='first')


class Rack(Base):
    """A representation of Rack in HTTP body"""

    id = int
    name = wtypes.text
    slots = int
    subnet = wtypes.text
    capacities = [wtypes.DictType(wtypes.text, wtypes.text)]

class ResourceClass(Base):
    """A representation of Resource Class in HTTP body"""

    id = int
    name = wtypes.text
    service_type = wtypes.text

class Blaa(Base):
    """A representation of a blaa."""

    uuid = wtypes.text
    description = wtypes.text

    @classmethod
    def sample(cls):
        return cls(uuid='c5255477-ed51-4017-91e0-0d96148f6937',
                   description="markmc's floury blaa")


class BlaaSausagesController(rest.RestController):
    """For GET /blaa/<blaa_id>/sausages."""

    @wsme_pecan.wsexpose([Sausage], unicode)
    def get(self, blaa_id):
        return [Sausage.from_db_model(r)
                for r in pecan.request.dbapi.get_sausages_by_blaa(blaa_id)]


class BlaasController(rest.RestController):
    """REST controller for Blaas."""

    @wsme.validate(Blaa)
    @wsme_pecan.wsexpose(Blaa, body=Blaa, status_code=201)
    def post(self, blaa):
        """Ceate a new blaa."""
        try:
            # FIXME(markmc): blaa doesn't have fields set
            blaa = Blaa(description=blaa.description, uuid=blaa.uuid)
            d = blaa.as_dict()
            r = pecan.request.dbapi.create_blaa(d)
        except Exception as e:
            LOG.exception(e)
            raise wsme.exc.ClientSideError(_("Invalid data"))
        return Blaa.from_db_model(r)

    @wsme_pecan.wsexpose([Blaa])
    def get_all(self):
        """Retrieve a list of all blaas."""
        # FIXME(markmc): columns?
        r = pecan.request.dbapi.get_blaas(None)
        return [Blaa.from_db_model(blaa) for blaa in r]

    @wsme_pecan.wsexpose(Blaa, unicode)
    def get_one(self, blaa_id):
        """Retrieve information about the given blaa."""
        r = pecan.request.dbapi.get_blaa(blaa_id)
        return Blaa.from_db_model(r)

    @wsme_pecan.wsexpose()
    def delete(self, blaa_id):
        """Delete a blaa."""
        pecan.request.dbapi.destroy_blaa(blaa_id)

    @wsme_pecan.wsexpose()
    def put(self, blaa_id):
        """Update a blaa."""
        pass

    sausages = BlaaSausagesController()


class RacksController(rest.RestController):
    """REST controller for Rack"""

    @wsme.validate(Rack)
    @wsme_pecan.wsexpose(Rack, body=Rack, status_code=201)
    def post(self, rack):
        """Create a new Rack."""
        try:
            new_rack = Rack(name=rack.name, slots=rack.slots,
                    subnet=rack.subnet, capacities=rack.capacities)
            d = new_rack.as_dict()
            result = pecan.request.dbapi.create_rack(d)
        except Exception as e:
            LOG.exception(e)
            raise wsme.exc.ClientSideError(_("Invalid data"))
        return Rack.from_db_model(result)

    @wsme_pecan.wsexpose([Rack])
    def get_all(self):
        """Retrieve a list of all racks"""
        result = pecan.request.dbapi.get_racks(None)
        return [Rack.from_db_model(rack) for rack in result]

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

    # TODO(markmc): _default and index
    # TODO(mfojtik): remove this at some point ;-)
    blaas = BlaasController()

    racks = RacksController()

    resource_classes = ResourceClassesController()