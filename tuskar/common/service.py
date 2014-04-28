#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright © 2012 eNovance <licensing@enovance.com>
#
# Author: Julien Danjou <julien@danjou.info>
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

import socket

from oslo.config import cfg
from oslo import messaging

from tuskar.common import rpc
from tuskar.openstack.common import context
from tuskar.openstack.common import log
from tuskar.openstack.common import service


cfg.CONF.register_opts([
    cfg.IntOpt('periodic_interval',
               default=60,
               help='seconds between running periodic tasks'),
    cfg.StrOpt('host',
               default=socket.getfqdn(),
               help='Name of this node.  This can be an opaque identifier.  '
               'It is not necessarily a hostname, FQDN, or IP address. '
               'However, the node name must be valid within '
               'an AMQP key, and if using ZeroMQ, a valid '
               'hostname, FQDN, or IP address'),
])


class RPCService(service.Service):
    def __init__(self, host, manager_module, manager_class):
        super(RPCService, self).__init__()
        self.host = host
        manager_module = importutils.import_module(manager_module)
        manager_class = getattr(manager_module, manager_class)
        self.manager = manager_class(host, manager_module.MANAGER_TOPIC)
        self.topic = self.manager.topic
        self.rpcserver = None

    def start(self):
        super(RPCService, self).start()
        admin_context = context.RequestContext('admin', 'admin', is_admin=True)
        self.tg.add_timer(cfg.CONF.periodic_interval,
                          self.manager.periodic_tasks,
                          context=admin_context)
        self.manager.init_host()
        LOG.debug(_("Creating RPC server for service %s"), self.topic)
        target = messaging.Target(topic=self.topic, server=self.host)
        endpoints = [self.manager]
        serializer = objects_base.IronicObjectSerializer()
        self.rpcserver = rpc.get_server(target, endpoints, serializer)
        self.rpcserver.start()

    def stop(self):
        super(RPCService, self).stop()
        try:
            self.rpcserver.stop()
            self.rpcserver.wait()
        except Exception as e:
            LOG.exception(_('Service error occurred when stopping the '
                            'RPC server. Error: %s'), e)
        try:
            self.manager.del_host()
        except Exception as e:
            LOG.exception(_('Service error occurred when cleaning up '
                            'the RPC manager. Error: %s'), e)

def prepare_service(argv=[]):
    rpc.set_defaults(control_exchange='tuskar')
    cfg.set_defaults(log.log_opts,
                     default_log_levels=['amqplib=WARN',
                                         'qpid.messaging=INFO',
                                         'sqlalchemy=WARN',
                                         'keystoneclient=INFO',
                                         'stevedore=INFO',
                                         'eventlet.wsgi.server=WARN',
                                         'iso8601=WARN'
                                         ])
    cfg.CONF(argv[1:], project='tuskar')
    log.setup('tuskar')
