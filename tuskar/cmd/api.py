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

"""The Tuskar Service API."""

import logging
import os
import sys

from oslo.config import cfg
from wsgiref import simple_server

from tuskar.api import app
from tuskar.common import service as tuskar_service
from tuskar.openstack.common import log

CONF = cfg.CONF


def main():
    # Pase config file and command line options, then start logging
    tuskar_service.prepare_service(sys.argv)

    # Build and start the WSGI app
    host = CONF.tuskar_api_bind_ip
    port = CONF.tuskar_api_port
    wsgi = simple_server.make_server(
            host, port,
            app.VersionSelectorApplication())

    LOG = log.getLogger(__name__)
    LOG.info("Serving on http://%s:%s" % (host, port))
    LOG.info("Configuration:")
    CONF.log_opt_values(LOG, logging.INFO)
    # make sure we have tripleo-heat-templates:
    heat_template_path = CONF.tht_local_dir
    try:
        templates = os.listdir(heat_template_path)
    except OSError:
        LOG.info("Can't find local tripleo-heat-template files at %s"
                  % (heat_template_path))
        LOG.info("Cannot proceed - missing tripleo heat templates " +
                  "See INSTALL documentation for more info")
        raise
    LOG.info("Using tripleo-heat-templates at %s" % (heat_template_path))

    try:
        wsgi.serve_forever()
    except KeyboardInterrupt:
        pass
