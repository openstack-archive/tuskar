#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
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

"""
The Tuskar Management Service
"""

import sys

from oslo.config import cfg

from tuskar.openstack.common import service

from tuskar.common import service as tuskar_service
from tuskar.manager import manager

CONF = cfg.CONF


def main():
    # Pase config file and command line options, then start logging
    tuskar_service.prepare_service(sys.argv)

    topic = 'tuskar.manager'
    mgr = manager.ManagerService(CONF.host, topic)
    launcher = service.launch(mgr)
    launcher.wait()
