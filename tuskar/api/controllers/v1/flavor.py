#from oslo.config import cfg
import pecan
#from pecan.core import render
from pecan import rest
import wsme
#from wsme import api
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

#from tuskar.common import exception
from tuskar.openstack.common import log

from tuskar.api.controllers.v1.types import Flavor

LOG = log.getLogger(__name__)


class FlavorsController(rest.RestController):
    """REST controller for Flavor."""

    #nova=NovaClient()

    #POST /api/resource_classes/1/flavors
    @wsme.validate(Flavor)
    @wsme_pecan.wsexpose(Flavor, wtypes.text, body=Flavor, status_code=201)
    def post(self, resource_class_id, flavor):
        """Create a new Flavor for a ResourceClass."""
        try:
            flavor = pecan.request.dbapi.create_resource_class_flavor(
                resource_class_id, flavor)
            #nova_flavor_uuid = self.nova.create_flavor(
            #    flavor,
            #    pecan.request.dbapi.get_resource_class(resource_class_id)
            #    .name
            #)
            #pecan.request.dbapi.update_flavor_nova_uuid(flavor.id,
            #                                            nova_flavor_uuid)
        except Exception as e:
            LOG.exception(e)
            raise wsme.exc.ClientSideError(_("Invalid data"))
        pecan.response.status_code = 201
        return Flavor.add_capacities(resource_class_id, flavor)

    #Do we need this, i.e. GET /api/resource_classes/1/flavors
    #i.e. return just the flavors for a given resource_class?
    @wsme_pecan.wsexpose([Flavor], wtypes.text)
    def get_all(self, resource_class_id):
        """Retrieve a list of all flavors."""
        flavors = []
        for flavor in pecan.request.dbapi.get_flavors(resource_class_id):
            flavors.append(Flavor.add_capacities(resource_class_id, flavor))

        return flavors
        #return [Flavor.from_db_model(flavor) for flavor in result]

    @wsme_pecan.wsexpose(Flavor, wtypes.text, wtypes.text)
    def get_one(self, resource_id, flavor_id):
        """Retrieve a specific flavor."""
        flavor = pecan.request.dbapi.get_flavor(flavor_id)
        return Flavor.add_capacities(resource_id, flavor)

    @wsme.validate(Flavor)
    @wsme_pecan.wsexpose(Flavor, wtypes.text, wtypes.text, body=Flavor)
    def put(self, resource_class_id, flavor_id, flavor):
        """Update an existing ResourceClass Flavor"""
        try:
            flavor = pecan.request.dbapi.update_resource_class_flavor(
                    resource_class_id, flavor_id, flavor)
        except Exception as e:
            LOG.exception(e)
            raise wsme.exc.ClientSideError(_("Invalid data"))
        return Flavor.add_capacities(resource_class_id, flavor)

    @wsme_pecan.wsexpose(None, wtypes.text, wtypes.text, status_code=204)
    def delete(self, resource_class_id, flavor_id):
        """Delete a Flavor."""
        #pecan.response.status_code = 204
        #nova_flavor_uuid = pecan.request.dbapi.delete_flavor(flavor_id)
        pecan.request.dbapi.delete_flavor(flavor_id)
        #self.nova.delete_flavor(nova_flavor_uuid)
