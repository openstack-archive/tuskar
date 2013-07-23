# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2013 Red Hat                # All Rights Reserved.

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#    Most of the following was copied shamelessly from nova @
#    https://github.com/openstack/nova/blob/master/nova/image/glance.py
#    It's the way nova talks to glance, though obviously
#    s/python-glanceclient/python-novaclient

#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""A client library for accessing Heat CloudFormations API using Boto"""

from oslo.config import cfg
from tuskar.openstack.common import log as logging

heat_opts = [

    cfg.StrOpt('heat_username',
               default='heat',
               help='Heat API username'),

    cfg.StrOpt('heat_password',
               default='heat',
               help='Heat API password'),

    cfg.StrOpt('heat_auth_url',
               default='http://10.34.32.181:35357/v2.0/',
               help='OpenStack Authentication URL (OS_AUTH_URL)'),

    cfg.StrOpt('heat_tenant_name',
               default='admin',
               help='Heat API tenant_id'),

    cfg.StrOpt('heat_stack_name',
               default='overcloud',
               help='Default Heat overcloud stack name'
               ),

    cfg.BoolOpt('heat_auth_url_insecure',
                default=True,
                help='Use HTTPs to speak with Heat'
                )
]

CONF = cfg.CONF
CONF.register_opts(heat_opts)
LOG = logging.getLogger(__name__)

from heatclient.v1.client import Client as heatclient
from keystoneclient.v2_0 import client as ksclient


class HeatClient(object):
    """Heat CloudFormations API client to use in Tuskar"""

    def __init__(self):
        kwargs = {
            'username': CONF.heat_username,
            'password': CONF.heat_password,
            'tenant_name': CONF.heat_tenant_name,
            'auth_url': CONF.heat_auth_url,
            'insecure': CONF.heat_auth_url_insecure,
        }

        def _get_ksclient(**kwargs):
            """ Setup the Keystone client """
            return ksclient.Client(username=kwargs.get('username'),
                                   password=kwargs.get('password'),
                                   tenant_name=kwargs.get('tenant_name'),
                                   auth_url=kwargs.get('auth_url'),
                                   insecure=kwargs.get('insecure'))

        def _get_endpoint(client, **kwargs):
            """ Get the Heat API endpoint from the Keystone """
            return client.service_catalog.url_for(
                service_type='orchestration',
                endpoint_type='publicURL')

        _ksclient = _get_ksclient(**kwargs)
        endpoint = _get_endpoint(_ksclient, **kwargs)

        self.connection = heatclient(endpoint=endpoint,
                                     token=_ksclient.auth_token)

    def validate_template(self, template_body):
        """Validate given Heat template"""
        try:
            self.connection.stacks.validate(template=template_body)
            return True
        except Exception as e:
            LOG.exception(e)
            return False

    def get_stack(self):
        """Get overcloud Heat template"""
        return self.connection.stacks.get(CONF.heat_stack_name)

    def get_template(self):
        """Get JSON representation of the Heat overcloud template"""
        return self.connection.stacks.template(stack_id=CONF.heat_stack_name)

    def update_stack(self, template_body, params):
        """Update the Heat overcloud stack"""
        try:
            self.connection.stacks.update(stack_id=CONF.heat_stack_name,
                                          template=template_body,
                                          parameters=params)
            return True
        except Exception as e:
            LOG.exception(e)
            return False
