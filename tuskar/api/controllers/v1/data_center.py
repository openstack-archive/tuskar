#from oslo.config import cfg
import pecan
#from pecan.core import render
from pecan import rest
import wsme
#from wsme import api
#from wsme import types as wtypes
#import wsmeext.pecan as wsme_pecan

from tuskar.compute.nova import NovaClient
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
        rcs = {'resource_categories': {'controller': 1, 'compute': 4,
                                        'object': 1, 'block': 2}}
        tuskar_template = template_tools.generate_template(rcs)
        overcloud = template_tools.merge_templates(tuskar_template)
        return overcloud

    @pecan.expose('json')
    def post(self):
        # TODO(): Currently all Heat parameters are hardcoded in
        #       template.
        params = {}
        rcs = pecan.request.dbapi.get_heat_data()
        heat = heat_client()
        nova_utils = NovaClient()

        for resource in rcs:
            service_type = resource.service_type
            image_id = getattr(resource, "image_id", None)

            if image_id:
                if service_type == 'compute':
                    params['NovaImage'] = image_id
                elif service_type in ('not_compute', 'controller'):
                    params['notcomputeImage'] = image_id

        tuskar_template = template_tools.generate_template(rcs)
        template_body = template_tools.merge_templates(tuskar_template)
        #template_body = render('overcloud.yaml', dict(resource_classes=rcs,
        #    nova_util=nova_utils))
        if heat.validate_template(template_body):

            if heat.exists_stack():
                res = heat.update_stack(template_body, params)
            else:
                res = heat.create_stack(template_body, params)

            if res:
                for rc in rcs:
                    [pecan.request.dbapi.update_rack_state(
                        r, 'CREATE_IN_PROGRESS') for r in rc.racks]

                pecan.response.status_code = 202
                return {}
            else:
                raise wsme.exc.ClientSideError(_(
                    "Cannot update the Heat overcloud template"
                ))
        else:
            raise wsme.exc.ClientSideError(_("The overcloud Heat template"
                                             "could not be validated"))
