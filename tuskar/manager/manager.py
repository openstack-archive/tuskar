# coding=utf-8

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

from tuskar.common import service
from tuskar.openstack.common import log
from tuskar.openstack.common import periodic_task

LOG = log.getLogger(__name__)


class ManagerService(periodic_task.PeriodicTasks):
    """Tuskar Manager Service.

    A single instance of this class is created within the tuskar-manager
    process.
    """

    def __init__(self, host, topic):
        super(ManagerService, self).__init__(host, topic)

    def start(self):
        super(ManagerService, self).start()
        # TODO(deva): connect with storage driver

    def initialize(self, service):
        LOG.debug(_('Manager initializing service hooks'))
        # TODO(deva)

    def process_notification(self, notification):
        LOG.debug(
            _('Received notification: %r') % notification.get('event_type'))
        # TODO(deva)

    def periodic_tasks(self, context):
        # TODO(deva)
        pass
