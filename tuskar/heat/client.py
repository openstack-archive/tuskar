# Copyright 2013 Red Hat                # All Rights Reserved.

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


#    Most of the following was copied shamelessly from nova @
#    https://github.com/openstack/nova/blob/master/nova/image/glance.py
#    It's the way nova talks to glance, though obviously
#    s/python-glanceclient/python-novaclient


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
    # TODO(rpodolyaka): https://bugs.launchpad.net/tuskar/+bug/1236703
    cfg.StrOpt('username',
               default=env.get('OS_USERNAME') or 'admin',
               help='The name of a user the overcloud is deployed on behalf of'
               ),
    cfg.StrOpt('password',
               help='The pass of a user the overcloud is deployed on behalf of'
               ),
    cfg.StrOpt('tenant_name',
               default=env.get('OS_TENANT_NAME') or 'admin',
               help='The tenant name the overcloud is deployed on behalf of'
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

from heatclient.exc import HTTPNotFound as HeatStackNotFound
from heatclient.v1.client import Client as heatclient
from keystoneclient.v2_0 import client as ksclient


class HeatClient(object):
    """Heat CloudFormations API client to use in Tuskar."""

    def __init__(self):
        try:
            keystone = ksclient.Client(**CONF.heat_keystone)
            endpoint = keystone.service_catalog.url_for(
                service_type=CONF.heat['service_type'],
                endpoint_type=CONF.heat['endpoint_type']
            )
            self.connection = heatclient(
                endpoint=endpoint,
                token=keystone.auth_token,
                username=CONF.heat_keystone['username'],
                password=CONF.heat_keystone['password'])
        except Exception:
            LOG.exception("An error occurred initialising the HeatClient")
            self.connection = None

    def validate_template(self, template_body):
        """Validate given Heat template."""
        return self.connection.stacks.validate(
            template=template_body)

    def get_stack(self, name=None):
        """Get overcloud Heat template."""
        if name is None:
            name = CONF.heat['stack_name']
        if self.connection:
            return self.connection.stacks.get(name)

    def get_template(self):
        """Get JSON representation of the Heat overcloud template."""
        return self.connection.stacks.template(
            stack_id=CONF.heat['stack_name']
        )

    def update_stack(self, template_body, params):
        """Update the Heat overcloud stack."""
        return self.connection.stacks.update(stack_id=CONF.heat['stack_name'],
                                             template=template_body,
                                             parameters=params)

    def delete_stack(self):
        """Delete the Heat overcloud stack."""
        return self.connection.stacks.delete(stack_id=CONF.heat['stack_name'])

    def create_stack(self, template_body, params):
        """Update the Heat overcloud stack."""
        return self.connection.stacks.create(
            stack_name=CONF.heat['stack_name'],
            template=template_body,
            parameters=params)

    def exists_stack(self, name=None):
        if name is None:
            name = CONF.heat['stack_name']
        try:
            self.get_stack(name)
            return True
        # return false if 404
        except HeatStackNotFound:
            return False
