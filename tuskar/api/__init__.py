# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
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

from oslo.config import cfg

API_SERVICE_OPTS = [
    cfg.StrOpt(
        'tuskar_api_bind_ip',
        default='0.0.0.0',
        help='IP for the Tuskar API server to bind to',
    ),
    cfg.IntOpt(
        'tuskar_api_port',
        default=8585,
        help='The port for the Tuskar API server',
    ),
    cfg.StrOpt(
        'tht_local_dir',
        default='/etc/tuskar/tripleo-heat-templates/',
        help='Local path holding tripleo-heat-templates',
    )
]

CONF = cfg.CONF
CONF.register_opts(API_SERVICE_OPTS)
