#!/usr/bin/env python
#
# Copyright 2012 eNovance <licensing@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import socket

from oslo_config import cfg
from oslo_log import log as logging

import tuskar.common.config  # noqa


cfg.CONF.register_opts([
    cfg.IntOpt('periodic_interval',
               default=60,
               help='seconds between running periodic tasks'),
    cfg.StrOpt('host',
               default=socket.getfqdn(),
               help='Name of this node. This can be an opaque identifier. '
               'It is not necessarily a hostname, FQDN, or IP address. '
               'However, the node name must be valid within '
               'an AMQP key, and if using ZeroMQ, a valid '
               'hostname, FQDN, or IP address'),
])


def prepare_service(argv=[]):
    logging.set_defaults(default_log_levels=['amqp=WARN',
                                             'amqplib=WARN',
                                             'qpid.messaging=INFO',
                                             'sqlalchemy=WARN',
                                             'keystoneclient=INFO',
                                             'stevedore=INFO',
                                             'eventlet.wsgi.server=WARN',
                                             'iso8601=WARN'
                                             ])
    cfg.CONF(argv[1:], project='tuskar')
    logging.setup(cfg.CONF, 'tuskar')
