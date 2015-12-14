#
# Copyright 2012 New Dream Network, LLC (DreamHost)
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

from keystonemiddleware import auth_token
from keystonemiddleware import opts
from oslo_config import cfg


def register_opts(conf):
    """Register keystonemiddleware options
    """
    for group, options in opts.list_auth_token_opts():
        conf.register_opts(list(options), group=group)
    auth_token.CONF = conf


def install(app, conf):
    """Install ACL check on application."""
    register_opts(cfg.CONF)
    return auth_token.AuthProtocol(app,
                                   conf=dict(conf.get(OPT_GROUP_NAME)))
