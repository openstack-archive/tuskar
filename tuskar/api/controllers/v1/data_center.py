#from oslo.config import cfg
import pecan
#from pecan.core import render
from pecan import rest
import wsme
#from wsme import api
#from wsme import types as wtypes
#import wsmeext.pecan as wsme_pecan

from tuskar.heat.client import HeatClient as heat_client
import tuskar.heat.template_tools as template_tools

#from tuskar.common import exception
#from tuskar.openstack.common import log


class DataCenterController(rest.RestController):
    """Controller for provisioning the Tuskar data centre description as an
    overcloud on Triple O
    """
    _custom_actions = {'template': ['GET']}

    @pecan.expose('json')
    def get_all(self):
        heat = heat_client()
        return heat.get_stack().to_dict()

    @pecan.expose()
    def template(self):
        #TODO(marios): what are we getting, exactly from the UI?
        #for now assuming:
        #
        #Look at review: /#/c/66062/. No more ResourceClasses...expecting
        #something like:
        # {
        #     'resource_categories': { 'controller': 1, 'compute': 4,
        #                                'object': 1, 'block': 2}
        # }
        #NO LONGER DOING THIS:
        #rcs = pecan.request.dbapi.get_heat_data()
        rcs = {'resource_categories': {'controller': 1, 'compute': 2}}
        #keep it super simple at first       'object': 1, 'block': 2}}
        #categories = pecan.request.dbapi.get_resource_categories()
        categories = []
        tuskar_template = template_tools.generate_template(rcs, categories)
        overcloud = template_tools.merge_templates(tuskar_template)
        return overcloud

    @pecan.expose('json')
    def post(self):
        #TODO(marios): what are we getting, exactly from the UI?
        #for now assuming:
        #
        #Look at review: /#/c/66062/. No more ResourceClasses...expecting
        #something like:
        # {
        #     'resource_categories': { 'controller': 1, 'compute': 4,
        #                                'object': 1, 'block': 2}
        # }
        #NO LONGER DOING THIS:
        #rcs = pecan.request.dbapi.get_heat_data()
        rcs = {'resource_categories': {'controller': 1, 'compute': 2}}
        #keep it super simple at first       'object': 1, 'block': 2}}
        #categories = pecan.request.dbapi.get_resource_categories()
        categories = []
        tuskar_template = template_tools.generate_template(rcs, categories)
        overcloud = template_tools.merge_templates(tuskar_template)
        heat = heat_client()
        #keeping this for now until heat client methods are reworked:
        params = {}
        if heat.validate_template(overcloud):
            if heat.exists_stack():
                res = heat.update_stack(overcloud, params)
            else:
                res = heat.create_stack(overcloud, params)

            if res:
                pecan.response.status_code = 202
                return {}
            else:
                raise wsme.exc.ClientSideError(_(
                    "Cannot update the Heat overcloud template"
                ))
        else:
            raise wsme.exc.ClientSideError(_("The overcloud Heat template"
                                             "could not be validated"))
