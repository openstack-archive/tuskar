#from oslo.config import cfg
import pecan
from pecan.core import render
from pecan import rest
import wsme
#from wsme import api
#from wsme import types as wtypes
#import wsmeext.pecan as wsme_pecan

from tuskar.compute.nova import NovaClient
from tuskar.heat.client import HeatClient as heat_client

#from tuskar.common import exception
#from tuskar.openstack.common import log
from oslo.config import cfg

overcloud_opts = [
    cfg.StrOpt('OVERCLOUD_ADMIN_TOKEN'),
    cfg.StrOpt('OVERCLOUD_ADMIN_PASSWORD'),
    cfg.StrOpt('OVERCLOUD_CINDER_PASSWORD'),
    cfg.StrOpt('OVERCLOUD_GLANCE_PASSWORD'),
    cfg.StrOpt('OVERCLOUD_HEAT_PASSWORD'),
    cfg.StrOpt('OVERCLOUD_NEUTRON_PASSWORD'),
    cfg.StrOpt('OVERCLOUD_NOVA_PASSWORD'),
    cfg.StrOpt('OVERCLOUD_DEMO_PASSWORD'),
    cfg.StrOpt('OVERCLOUD_LIBVIRT_TYPE')
]

CONF = cfg.CONF
CONF.register_opts(overcloud_opts, group='overcloud')

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
        rcs = pecan.request.dbapi.get_heat_data()
        nova_utils = NovaClient()
        return render('overcloud.yaml', dict(resource_classes=rcs,
                                             nova_util=nova_utils))

    @pecan.expose('json')
    def post(self):
        # TODO(): Currently all Heat parameters are hardcoded in
        #       template.
        params = {}
        params['AdminToken']=CONF.overcloud['OVERCLOUD_ADMIN_TOKEN']
        params['AdminPassword']=CONF.overcloud['OVERCLOUD_ADMIN_PASSWORD']
        params['CinderPassword']=CONF.overcloud['OVERCLOUD_CINDER_PASSWORD']
        params['GlancePassword']=CONF.overcloud['OVERCLOUD_GLANCE_PASSWORD']
        params['HeatPassword']=CONF.overcloud['OVERCLOUD_HEAT_PASSWORD']
        params['NeutronPassword']=CONF.overcloud['OVERCLOUD_NEUTRON_PASSWORD']
        params['NovaPassword']=CONF.overcloud['OVERCLOUD_NOVA_PASSWORD']
        params['NovaComputeLibvirtType']=CONF.overcloud['OVERCLOUD_LIBVIRT_TYPE']

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

        template_body = render('overcloud.yaml', dict(resource_classes=rcs,
            nova_util=nova_utils))
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
