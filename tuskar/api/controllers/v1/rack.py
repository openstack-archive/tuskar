#from oslo.config import cfg

import pecan
#from pecan.core import render
from pecan import rest

import wsme
from wsme import api
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from tuskar.api.controllers.v1.types import Error
from tuskar.api.controllers.v1.types import Link
from tuskar.api.controllers.v1.types import Rack
from tuskar.common import exception
#from tuskar.compute.nova import NovaClient
from tuskar.heat.client import HeatClient as heat_client
from tuskar.openstack.common import log

LOG = log.getLogger(__name__)


class RacksController(rest.RestController):
    """REST controller for Rack."""

    @wsme.validate(Rack)
    @wsme_pecan.wsexpose(Rack, body=Rack, status_code=201)
    def post(self, rack):
        """Create a new Rack."""
        try:
            result = pecan.request.dbapi.create_rack(rack)
            links = [Link.build('self',
                                pecan.request.host_url,
                                'racks',
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

    @wsme.validate(Rack)
    @wsme_pecan.wsexpose(Rack, wtypes.text, body=Rack, status_code=200)
    def put(self, rack_id, rack):
        """Update the Rack."""

        try:
            result = pecan.request.dbapi.update_rack(rack_id, rack)
            links = [Link.build('self', pecan.request.host_url, 'racks',
                                result.id)]
            #
            # TODO(mfojtik): Update the HEAT template at this point
            #
        except Exception as e:
            LOG.exception(e)
            raise wsme.exc.ClientSideError(_("Invalid data"))
        return Rack.convert_with_links(result, links)

    @wsme_pecan.wsexpose([Rack])
    def get_all(self):
        """Retrieve a list of all racks."""
        result = []
        links = []
        db_api = pecan.request.dbapi
        heat_stack = False
        if heat_client().exists_stack():
            heat_stack = heat_client().get_stack()

        for rack in db_api.get_racks(None):
            if heat_stack:
                db_api.update_rack_state(rack, heat_stack.stack_status)
            links = [Link.build('self', pecan.request.host_url, 'racks',
                                rack.id)]
            result.append(Rack.convert_with_links(rack, links))

        return result

    @wsme_pecan.wsexpose(Rack, unicode)
    def get_one(self, rack_id):
        """Retrieve information about the given Rack."""
        db_api = pecan.request.dbapi
        try:
            rack = db_api.get_rack(rack_id)
        except exception.TuskarException as e:
            response = api.Response(
                None,
                error=Error(faultcode=e.code, faultstring=str(e)),
                status_code=e.code)
            return response

        heat_stack = False
        if heat_client().exists_stack():
            heat_stack = heat_client().get_stack()

        if heat_stack:
            db_api.update_rack_state(rack, heat_stack.stack_status)
        links = [Link.build('self', pecan.request.host_url, 'racks',
                            rack.id)]
        return Rack.convert_with_links(rack, links)

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, rack_id):
        """Remove the Rack."""
        try:
            pecan.request.dbapi.delete_rack(rack_id)
            pecan.response.status_code = 204
            #
            # TODO(mfojtik): Update the HEAT template at this point
            #
        except exception.TuskarException as e:
            response = api.Response(
                Error(faultcode=e.code, faultstring=str(e)),
                status_code=e.code)
            return response
