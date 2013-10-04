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
import sys

from oslo.config import cfg
import os
from wsgiref import simple_server

from tuskar.api import app
from tuskar.common import service as tuskar_service
from tuskar.openstack.common import log

CONF = cfg.CONF

def fetch_remote_heat_templates(template_path):
    template_git = CONF.tht_git_repo
    os.system("cd "+template_path+" ; git clone "+template_git)
    #HAX: revert to a specific known-working commit for HK/freeze:
    #uncomment next 3 lines to use:
    # commit_id="0326335160a5977df44ae40d4c81ab8e40833743"
    # os.system("cd "+template_path+"/tripleo-heat-templates; git "+
    #           "reset --hard "+ commit_id )

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
    heat_template_path = CONF.tht_local_dir +"tripleo-heat-templates"
    try:
        templates = os.listdir(heat_template_path)
        if len(templates) < 1:
            LOG.info("Can't find your local tripleo-heat-templates at "+
                     heat_template_path+". Pulling from git repo at " +
                     CONF.tht_git_repo)
            fetch_remote_heat_templates(CONF.tht_local_dir)
    except OSError:
            LOG.info("Can't find your local tripleo-heat-template directory "+
                     "at "+CONF.tht_local_dir + ". Pulling from git repo "+
                     "at "+CONF.tht_git_repo)
            fetch_remote_heat_templates(CONF.tht_local_dir)
    LOG.info("Working with tripleo-heat-templates at"+heat_template_path)

    try:
        wsgi.serve_forever()
    except KeyboardInterrupt:
        pass
