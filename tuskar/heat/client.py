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

from os import environ as env
from oslo.config import cfg
from tuskar.openstack.common import log as logging

heat_opts = [
    cfg.StrOpt('stack_name',
               default='overcloud',
               help='Name of the overcloud Heat stack'
               ),
    cfg.StrOpt('service_type',
               default='orchestration',
               help='Heat API service type registered in keystone'
               ),
    cfg.StrOpt('endpoint_type',
               default='publicURL',
               help='Heat API service endpoint type in keystone'
               )
]

heat_keystone_opts = [
    cfg.StrOpt('username',
               default=env.get('OS_USERNAME') or 'heat',
               help='Heat API username'
               ),
    cfg.StrOpt('password',
               default=env.get('OS_PASSWORD') or 'heat',
               help='Heat API user password'
               ),
    cfg.StrOpt('tenant_name',
               default=env.get('OS_TENANT_NAME') or 'admin',
               help='Heat API keystone tenant name'
               ),
    cfg.StrOpt('auth_url',
               default=env.get('OS_AUTH_URL') or 'http://localhost:35357/v2.0',
               help='Keystone authentication URL'
               ),
    cfg.BoolOpt('insecure',
               default=True,
               help='Set to False when Heat API uses HTTPS'
               )
]

CONF = cfg.CONF
CONF.register_opts(heat_opts, group='heat')
CONF.register_opts(heat_keystone_opts, group='heat_keystone')
LOG = logging.getLogger(__name__)

from heatclient.v1.client import Client as heatclient
from keystoneclient.v2_0 import client as ksclient


class HeatClient(object):
    """Heat CloudFormations API client to use in Tuskar"""

    def __init__(self):
        try:
            keystone = ksclient.Client(**CONF.heat_keystone)
            endpoint = keystone.service_catalog.url_for(
                    service_type=CONF.heat['service_type'],
                    endpoint_type=CONF.heat['endpoint_type'])
            self.connection = heatclient(endpoint=endpoint,
                                         token=keystone.auth_token)
        except Exception as e:
            LOG.exception(e)
            raise e

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
        return self.connection.stacks.get(CONF.heat['stack_name'])

    def get_template(self):
        """Get JSON representation of the Heat overcloud template"""
        return self.connection.stacks.template(
                stack_id=CONF.heat['stack_name']
                )

    def update_stack(self, template_body, params):
        """Update the Heat overcloud stack"""
        try:
            self.connection.stacks.update(stack_id=CONF.heat['stack_name'],
                                          template=template_body,
                                          parameters=params)
            return True
        except Exception as e:
            LOG.exception(e)
            return False
