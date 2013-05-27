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
Version 1 of the Ironic API

Should maintain feature parity with Nova Baremetal Extension.
Specification in ironic/doc/api/v1.rst
"""

import pecan
from pecan import rest

import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from ironic.openstack.common import log

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


class Controller(object):
    """Version 1 API controller root."""

    # TODO(markmc): _default and index

    blaas = BlaasController()
