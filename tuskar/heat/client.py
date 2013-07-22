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
import xml.etree.ElementTree as ET

heat_opts = [
        cfg.StrOpt('boto_config',
            default='etc/tuskar/boto.conf',
            help='Location of the Boto configuration file'),
        cfg.IntOpt('heat_cfn_port',
            default=8000,
            help='Heat CloudFormations API port'),
        cfg.StrOpt('heat_cfn_path',
            default='/v1',
            help='Heat CloudFormations API entrypoint URI')
]

CONF = cfg.CONF
CONF.register_opts(heat_opts)

# You can overide the 'boto_config' using BOTO_CONFIG environment variable.
#
os.environ['BOTO_CONFIG'] = CONF.boto_config
import boto
from boto.cloudformation import CloudFormationConnection

boto.log = logging.getLogger(__name__)

class HeatClient(object):
    """Heat CloudFormations API client to use in Tuskar"""

    def __init__(self):
        self.connection = CloudFormationConnection(port=CONF.heat_cfn_port,
                path=CONF.heat_cfn_path, debug=2)

    def validate_template(self, template_body):
        try:
            self.connection.validate_template(template_body)
            return True
        except BotoServerError:
            return False


    def register_template(self, name, template_body, params):
        return self.connection.create_stack(name,
                template_body=template_body,parameters=params)

    def get_template(self, template_id):
        return self.connection.get_template(template_id)

    def delete_template(self, template_id):
        return self.connection.delete_stack(template_id)
