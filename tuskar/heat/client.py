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

import os
from oslo.config import cfg
from tuskar.openstack.common import log as logging

heat_opts = [
        cfg.StrOpt('boto_config',
            default='etc/tuskar/boto.conf',
            help='Location of the Boto configuration file'),
        cfg.IntOpt('heat_cfn_port',
            default=8000,
            help='Heat CloudFormations API port'),
        cfg.StrOpt('heat_cfn_path',
            default='/v1',
            help='Heat CloudFormations API entrypoint URI'),
        cfg.StrOpt('heat_stack_name',
            default='overcloud',
            help='Default Heat overcloud stack name'
            )
]

CONF = cfg.CONF
CONF.register_opts(heat_opts)

# You can overide the 'boto_config' using BOTO_CONFIG environment variable.
#
os.environ['BOTO_CONFIG'] = CONF.boto_config
import boto
from boto.exception import BotoServerError
from boto.cloudformation import CloudFormationConnection

boto.log = logging.getLogger(__name__)


class HeatClient(object):
    """Heat CloudFormations API client to use in Tuskar"""

    def __init__(self):
        # TODO: The debug here is set to be super-verbose.
        #       This should be set to 0 when in production.
        #
        self.connection = CloudFormationConnection(port=CONF.heat_cfn_port,
                path=CONF.heat_cfn_path, debug=2)

    def validate_template(self, template_body):
        """Validate given Heat template"""
        try:
            self.connection.validate_template(template_body)
            return True
        except BotoServerError as e:
            boto.log.exception(e)
            return False

    def get_stack(self):
        """Get overcloud Heat template"""
        try:
            return self.connection.describe_stacks(CONF.heat_stack_name)[0]
        except Exception as e:
            boto.log.exception(e)
            return False

    def get_template(self):
        """Get JSON representation of the Heat overcloud template"""
        try:
            template_json = self.connection.get_template(
                    CONF.heat_stack_name)['GetTemplateResponse']
            return template_json['GetTemplateResult']['TemplateBody']
        except BotoServerError as e:
            boto.log.exception(e)
            return False

    def update_stack(self, template_body, params):
        """Update the Heat overcloud stack"""
        return self.connection.update_stack(CONF.heat_stack_name,
                template_body=template_body, parameters=params)
