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
ROLES[OVERCLOUD_CONTROL_ROLE] = {
    'template_param': 'Control',
    'flavor_param': 'OvercloudControlFlavor', }
ROLES[OVERCLOUD_COMPUTE_ROLE] = {
    'template_param': 'NovaCompute',
    'flavor_param': 'OvercloudComputeFlavor', }
ROLES[OVERCLOUD_VOLUME_ROLE] = {
    'template_param': 'BlockStorage',
    'flavor_param': 'OvercloudBlockStorageFlavor', }
ROLES[OVERCLOUD_OBJECT_STORAGE_ROLE] = {
    'template_param': 'SwiftStorage',
    'flavor_param': 'OvercloudSwiftStorageFlavor', }


def generate_scaling_params(overcloud_roles):
    """Given a dictionary containing a key value mapping of Overcloud Role name
    to a count of the nodes return the scaling parameters to be used by
    tripleo_heat_merge

    :param overcloud_roles: Dictionary with role names and a count of the nodes
    :type  overcloud_roles: dict

    :return: scaling parameters dict
    :rtype:  dict
    """

    # Default values, merge.py needs also the 0 counts.
    scaling_defaults = ['NovaCompute=0', 'SwiftStorage=0', 'BlockStorage=0']

    scaling = merge.parse_scaling(scaling_defaults)

    for overcloud_role, count in overcloud_roles.items():
        overcloud_role = overcloud_role.lower()
        if overcloud_role in ROLES:
            scale_str = "%s=%s" % (
                        ROLES[overcloud_role]['template_param'], count)
            scaling.update(merge.parse_scaling([scale_str]))

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
    overcloud_source = _join_template_path("overcloud-source.yaml")
    block_storage = _join_template_path("block-storage.yaml")
    swift_source = _join_template_path("swift-source.yaml")
    swift_storage_source = _join_template_path("swift-storage-source.yaml")
    ssl_src_path = _join_template_path("ssl-source.yaml")
    swift_deploy = _join_template_path("swift-deploy.yaml")
    nova_compute_config = _join_template_path("nova-compute-config.yaml")

    # Adding all templates like in tripleo-heat-templates Makefile.
    # They will be used by merge.py according to scale_params. So the
    # decision what template to pick will not be here.
    merged_paths = [overcloud_source, block_storage, swift_source,
                    swift_storage_source, ssl_src_path, swift_deploy,
                    nova_compute_config]

    template = merge.merge(merged_paths, None, None,
                           included_template_dir=cfg.CONF.tht_local_dir,
                           scaling=scale_params)

    return template
