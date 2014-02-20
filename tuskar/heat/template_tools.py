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

"""
Utilities for using merge.py to generate overcloud.yaml to hand over to Heat.
Translates Tuskar resources into the overcloud heat template, using merge.py
from upstream tripleo-heat-templates.
"""

import os

from oslo.config import cfg
from tripleo_heat_merge import merge


# The name of the compute Overcloud role - defined for special case handling
OVERCLOUD_COMPUTE_ROLE = 'overcloud-compute'
OVERCLOUD_VOLUME_ROLE = 'overcloud-cinder-volume'
ROLES = {}
ROLES[OVERCLOUD_COMPUTE_ROLE] = {'template_param': 'NovaCompute',
                                 'file_name': 'overcloud-source.yaml'}
ROLES[OVERCLOUD_VOLUME_ROLE] = {'template_param': 'BlockStorage',
                                'file_name': 'block-storage.yaml'}


def generate_scaling_params(overcloud_roles):
    """Given a dictionary containing a key value mapping of Overcloud Role name
    to a count of the nodes return the scaling parameters to be used by
    tripleo_heat_merge

    :param overcloud_roles: Dictionary with role names and a count of the nodes
    :type  overcloud_roles: dict

    :return: scaling parameters dict
    :rtype:  dict
    """

    scaling = {}

    for overcloud_role, count in overcloud_roles.items():
        overcloud_role = overcloud_role.lower()
        if overcloud_role in ROLES.keys():
            scale_str = "%s=%s" % (
                        ROLES[overcloud_role]['template_param'], count)
            scaling = dict(
                scaling.items() +
                merge.parse_scaling([scale_str]).items()
            )
    return scaling


def _join_template_path(file_name):
    return os.path.abspath(
        os.path.join(os.path.dirname(cfg.CONF.tht_local_dir), file_name)
    )


def merge_templates(overcloud_roles):
    """Merge the Overcloud Roles with overcloud.yaml using merge from
    tripleo_heat_merge

    See tripleo-heat-templates for further details.
    """

    # TODO(dmatthews): Add exception handling to catch merge errors

    scale_params = generate_scaling_params(overcloud_roles)
    overcloud_src_path = _join_template_path("overcloud-source.yaml")
    block_storage_path = _join_template_path(
        ROLES[OVERCLOUD_VOLUME_ROLE]['file_name'])
    ssl_src_path = _join_template_path("ssl-source.yaml")
    swift_src_path = _join_template_path("swift-source.yaml")
    merge_paths = [overcloud_src_path, ssl_src_path, swift_src_path]
    if OVERCLOUD_VOLUME_ROLE in overcloud_roles.keys():
        if overcloud_roles[OVERCLOUD_VOLUME_ROLE] > 0:
            merge_paths.append(block_storage_path)
    template = merge.merge(merge_paths, None, None,
                           included_template_dir=cfg.CONF.tht_local_dir,
                           scaling=scale_params)

    return template
