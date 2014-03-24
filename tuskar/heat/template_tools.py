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


# TODO(lsmola) For now static definition of roles for Icehouse
# we will need to load these associations from somewhere.
OVERCLOUD_CONTROL_ROLE = 'overcloud-control'
OVERCLOUD_COMPUTE_ROLE = 'overcloud-compute'
OVERCLOUD_VOLUME_ROLE = 'overcloud-cinder-volume'
OVERCLOUD_OBJECT_STORAGE_ROLE = 'overcloud-swift-storage'

ROLES = {}
ROLES[OVERCLOUD_CONTROL_ROLE] = {'template_param': 'Control',
                                 'flavor_param': 'OvercloudControlFlavor',
                                 'file_name': None}
ROLES[OVERCLOUD_COMPUTE_ROLE] = {'template_param': 'NovaCompute',
                                 'flavor_param': 'OvercloudComputeFlavor',
                                 'file_names': ['overcloud-source.yaml']}
ROLES[OVERCLOUD_VOLUME_ROLE] = {'template_param': 'BlockStorage',
                                'flavor_param': 'OvercloudBlockStorageFlavor',
                                'file_names': ['block-storage.yaml']}
ROLES[OVERCLOUD_OBJECT_STORAGE_ROLE] = {
    'template_param': 'SwiftStorage',
    'flavor_param': 'OvercloudSwiftStorageFlavor',
    'file_names': ['swift-source.yaml', 'swift-storage-source.yaml']}


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
        if overcloud_role in ROLES:
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


def merge_paths(merged_paths, overcloud_roles, role):
    if role in overcloud_roles:
        if overcloud_roles[role] > 0:
            paths = [_join_template_path(file_name) for file_name
                     in ROLES[role]['file_names']]
            return merged_paths + paths

    return merged_paths


def merge_templates(overcloud_roles):
    """Merge the Overcloud Roles with overcloud.yaml using merge from
    tripleo_heat_merge

    See tripleo-heat-templates for further details.
    """

    # TODO(dmatthews): Add exception handling to catch merge errors

    scale_params = generate_scaling_params(overcloud_roles)
    overcloud_src_path = _join_template_path("overcloud-source.yaml")
    ssl_src_path = _join_template_path("ssl-source.yaml")
    merged_paths = [overcloud_src_path, ssl_src_path]

    merged_paths = merge_paths(merged_paths, overcloud_roles,
                               OVERCLOUD_OBJECT_STORAGE_ROLE)
    merged_paths = merge_paths(merged_paths, overcloud_roles,
                               OVERCLOUD_VOLUME_ROLE)

    template = merge.merge(merged_paths, None, None,
                           included_template_dir=cfg.CONF.tht_local_dir,
                           scaling=scale_params)

    return template
