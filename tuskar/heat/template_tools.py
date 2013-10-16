# Copyright (c) 2013 Red Hat
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
    Util for using merge.py to generate overcloud.yaml to hand over to Heat.
    Translates Tuskar resources into the overcloud heat template, using
    merge.py from upstream tripleo-heat-templates """

import os

from oslo.config import cfg
from tripleo_heat_merge import merge as tht_merge

CONF = cfg.CONF
template_path = CONF.tht_local_dir
compute_path = os.path.abspath(os.path.join(template_path,
                                "nova-compute-instance.yaml"))
controller_path = os.path.abspath(os.path.join(template_path,
                                "notcompute.yaml"))
object_path = os.path.abspath(os.path.join(template_path,
                                "swift-source.yaml"))
block_path = os.path.abspath(os.path.join(template_path,
                                "block-storage.yaml"))

COMPUTE_CONFIG = ''


def generate_scaling_params(rcs):
    scaling = {}
    for rc, count in rcs['overcloud_roles'].items():
        rc = rc.lower()
        if rc == 'compute':
            scaling = dict(scaling.items() +
                tht_merge.parse_scaling(["NovaCompute=%s" % (count)]).items())
    return scaling


def merge_templates(rcs):
    """Merge with overcloud.yaml using merge.py.

    See tripleo-heat-templates.
    """
    scale_params = generate_scaling_params(rcs)
    overcloud_src_path = os.path.abspath(os.path.join(os.path.dirname(
                                  template_path), "overcloud-source.yaml"))
    ssl_src_path = os.path.abspath(os.path.join(os.path.dirname(
                                  template_path), "ssl-source.yaml"))
    swift_src_path = os.path.abspath(os.path.join(os.path.dirname(
                                  template_path), "swift-source.yaml"))

    template = tht_merge.merge(
        [overcloud_src_path, ssl_src_path, swift_src_path], None, None,
        included_template_dir=template_path, scaling=scale_params)
    return template
