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
In Juno, Tuskar supports the aggregation of resource providers into a
deployment plan. The TripleO Heat Templates, however, require more
advanced handling than will not be present in the Juno release.

The THT templates use resources at the top level of overcloud.yaml to
generate property values used across multiple provider resources. Additionally,
these values require their own input parameters and are used in the stack
outputs. Ultimately, Tuskar will support adding these resources in a similar
way as adding a role to a plan. This work is planned for Kilo.

For Juno, a Tuskar user can specify a seed master template file during the
role loading process. This file references the possible roles as well as any
other parameters, resources, and outputs that should be included in *all*
created plans. Without overcomplicating things by overusing the word, the
seed is a template for how the plan's master template will look.

This module contains methods to make the appropriate additions to a deployment
plan's master template file using a seed template.
"""

import copy
import logging

from tuskar.templates.heat import EnvironmentParameter
from tuskar.templates.heat import Resource


LOG = logging.getLogger(__name__)


def add_top_level_resources(source, destination):
    """Adds the top-level resources from the source template into the given
    template. If the resource is already in the destination template, it
    will not be added again.

    :type source: tuskar.templates.heat.Template
    :type destination: tuskar.templates.heat.Template
    """
    top_level_resources = [r for r in source.resources if not _is_role(r)]

    for r in top_level_resources:
        if destination.find_resource_by_id(r.resource_id) is None:
            cloned = copy.copy(r)
            destination.add_resource(cloned)


def add_top_level_parameters(source, destination, environment):
    """Adds the top-level parameters from the source template into the given
    template. If the parameter is already in the destination template, it will
    not be added again.

    :type source: tuskar.templates.heat.Template
    :type destination: tuskar.templates.heat.Template
    :type environment: tuskar.templates.heat.Environment
    """

    # Make a list of all property key names across all role resources
    role_property_names = []

    def _resource_property_keys(resource):
        keys = []

        for rp in resource.properties:
            if rp.name in ('resource_def', 'resource'):
                # For a resource definition, dig into the properties value
                # within to get all of the inner resource properties.
                for name in rp.value['properties']:
                    keys.append(name)
            else:
                # For all other resource properties, if the value is a
                # get_param lookup, consider the value of the look up a
                # resource property.
                if isinstance(rp.value, dict) and 'get_param' in rp.value:
                    keys.append(rp.value['get_param'])
        return keys

    role_resources = [r for r in source.resources if _is_role(r)]
    for r in role_resources:
        names = _resource_property_keys(r)
        role_property_names.extend(names)

    # Get the list of all source parameters and strip out any that came from
    # a role
    top_level_params = [p for p in source.parameters
                        if p.name not in role_property_names]

    # Add a copy of each top-level parameter to the destination if it's not
    # already present
    for p in top_level_params:
        if destination.find_parameter_by_name(p.name) is None:
            cloned = copy.copy(p)
            destination.add_parameter(cloned)

            ep = EnvironmentParameter(p.name, p.default or '')
            environment.add_parameter(ep)


def add_top_level_outputs(source, destination):
    """Adds all top-level outputs from the source template into the given
    template. If the output is already in the destination, it will not be
    added again.

    :type source: tuskar.templates.heat.Template
    :type destination: tuskar.templates.heat.Template
    """
    for o in source.outputs:
        if destination.find_output_by_name(o.name) is None:
            cloned = copy.copy(o)
            destination.add_output(cloned)


def get_property_map_for_role(source, role_name):
    """Returns a mapping of property name to the specific value that should
    be used for it in the corresponding resource in the master template. For
    properties not returned in this way, Tuskar will create a master template
    parameter and a get_param lookup when creating the role resource.

    :type source: tuskar.templates.heat.Template
    :param role_name: non-namespaced role name
    :type  role_name: str

    :return: mapping of property name to top-level resource lookup (get_attr)
             for any complex property in the role; simple properties will not
             be present in the dict; None if the role is not found in the
             source template
    :rtype:  dict

    :raises ValueError: if the role is not in the given template
    """
    resource = _find_resource_by_case_insensitive_id(source.resources,
                                                     role_name)

    if resource is None:
        return None

    property_map = {}
    resource_def = resource.find_property_by_name('resource_def')
    for name, value in resource_def.value['properties'].items():
        # If the property is a straight get_param look up, there is nothing
        # special to map. Tuskar will take care of adding these when the
        # role is added.
        if isinstance(value, dict) and 'get_param' in value:
            continue

        property_map[name] = value

    return property_map


def update_references(template, seed_role_name, tuskar_resource_name):
    """Updates the global resources in the given template to change references
    inside of the top-level resources from the seed's role name to the
    name of the resource as added by Tuskar.

    For example, the overcloud.yaml definition for the compute resource is
    given the name "Compute", however when Tuskar generates the resource it
    includes the role and version information and is named
    "compute-1-servers".

    Many of the top-level resources will want to reference the role in its
    properties using one of two mechanisms: get_attr or get_resource. In
    these cases, the lookup must be changed to the Tuskar-generated role name.

    :type template: tuskar.templates.heat.Template
    :type seed_role_name: str
    :type tuskar_resource_name: str
    """
    top_level_resources = [r for r in template.resources if not _is_role(r)]

    def index_property(update_me):
        if isinstance(update_me, dict):
            return update_me.items()
        elif isinstance(update_me, list):
            return enumerate(update_me)

    def update_property(update_me):
        for index, value in index_property(update_me):
            if isinstance(value, (dict, list)):
                update_property(value)
            elif isinstance(value, basestring):
                if value.lower() == seed_role_name.lower():
                    update_me[index] = tuskar_resource_name
            else:
                LOG.warn('Unexpected type (%s) in property value (%s)' %
                         (value.__class__.__name__, value))

    for r in top_level_resources:
        for p in r.properties:
            if isinstance(p.value, dict):
                update_property(p.value)


def _is_role(resource):
    """Returns whether or not the given resource represents a role.

    :type resource: tuskar.templates.heat.Resource
    :rtype: bool
    """
    scaling_groups = ('OS::Heat::ResourceGroup', 'OS::Heat::AutoScalingGroup')
    if resource.resource_type in scaling_groups:
        inner_resource = resource.find_property_by_name('resource_def')

        if isinstance(inner_resource.value, Resource):
            v = inner_resource.value.resource_type
        else:
            v = inner_resource.value['type']

        return 'OS::TripleO::' in v
    else:
        return False


def _find_resource_by_case_insensitive_id(resources, resource_id):
    """Returns the resource or None if it is not found. While it is
    technically possible that the template contains multiple resources with
    the given ID in different cases, it's not likely. For safety, this method
    will raise an error if that occurs.

    :type resources: list of tuskar.templates.heat.Resource
    :str resource_id: str
    :rtype: tuskar.templates.heat.Resource
    :raise ValueError: if the template contains more than one resource with
                       the given ID (regardless of case)
    """
    resource_id = resource_id.lower()
    matching = [r for r in resources if r.resource_id.lower() == resource_id]

    if len(matching) > 1:
        raise ValueError('Invalid template; contains multiple resources '
                         'matching %s' % resource_id)
    elif len(matching) == 1:
        return matching[0]
    else:
        return None
