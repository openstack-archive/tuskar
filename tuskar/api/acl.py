#
# Copyright 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Access Control Lists (ACL's) control access the API server."""

from keystoneclient.middleware import auth_token
from oslo.config import cfg


OPT_GROUP_NAME = 'keystone_authtoken'


def register_opts(conf):
    """Register keystoneclient middleware options
    """
    conf.register_opts(auth_token.opts, group=OPT_GROUP_NAME)
    auth_token.CONF = conf


def install(app, conf):
    """Install ACL check on application."""
    register_opts(cfg.CONF)
    return auth_token.AuthProtocol(app,
                                   conf=dict(conf.get(OPT_GROUP_NAME)))
