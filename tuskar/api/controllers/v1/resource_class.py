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

from tuskar.api.controllers.v1.flavor import FlavorsController
#from tuskar.api.controllers.v1.types import Base
#from tuskar.api.controllers.v1.types import Flavor
#from tuskar.api.controllers.v1.types import Relation
from tuskar.api.controllers.v1.types import ResourceClass

LOG = log.getLogger(__name__)


class ResourceClassesController(rest.RestController):
    """REST controller for Resource Class."""

    flavors = FlavorsController()

    @wsme.validate(ResourceClass)
    @wsme_pecan.wsexpose(ResourceClass, body=ResourceClass, status_code=201)
    def post(self, resource_class):
        """Create a new Resource Class."""
        try:
            result = pecan.request.dbapi.create_resource_class(resource_class)
            #create in nova any flavors included in this resource_class
            #creation for flav in result.flavors:
            #nova_flavor_uuid = self.flavors.nova.create_flavor(flav,
            #                                                   result.name)
            #pecan.request.dbapi.update_flavor_nova_uuid(flav.id,
            #                                            nova_flavor_uuid)
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

    @wsme.validate(ResourceClass)
    @wsme_pecan.wsexpose(ResourceClass, wtypes.text, body=ResourceClass,
                         status_code=200)
    def put(self, resource_class_id, resource_class):
        try:
            result = pecan.request.dbapi.update_resource_class(
                resource_class_id,
                resource_class)
            #
            # TODO(mfojtik): Update the HEAT template at this point
            #
        except Exception as e:
            LOG.exception(e)
            raise wsme.exc.ClientSideError(_("Invalid data"))
        return ResourceClass.convert(result, pecan.request.host_url)

    @wsme_pecan.wsexpose([ResourceClass])
    def get_all(self):
        """Retrieve a list of all Resource Classes."""
        result = []
        for rc in pecan.request.dbapi.get_resource_classes(None):
            result.append(ResourceClass.convert(rc, pecan.request.host_url))

        return result

    @wsme_pecan.wsexpose(ResourceClass, unicode)
    def get_one(self, resource_class_id):
        """Retrieve information about the given Resource Class."""
        dbapi = pecan.request.dbapi
        resource_class = dbapi.get_resource_class(resource_class_id)
        return ResourceClass.convert(resource_class, pecan.request.host_url)

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, resource_class_id):
        """Remove the Resource Class."""
        #
        # TODO(mfojtik): Update the HEAT template at this point
        #
        #DELETE any resource class flavors from nova too
        #for flav in pecan.request.dbapi.get_flavors(resource_class_id):
        #    nova_flavor_uuid = pecan.request.dbapi.delete_flavor(flav.id)
        #    self.flavors.nova.delete_flavor(nova_flavor_uuid)
        pecan.request.dbapi.delete_resource_class(resource_class_id)
