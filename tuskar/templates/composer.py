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
Functionality for converting Tuskar domain models into their Heat-acceptable
formats.

These functions are written against the HOT specification found at:
http://docs.openstack.org/developer/heat/template_guide/hot_spec.html
"""

import yaml

from tuskar.templates.heat import Resource


def compose_template(template):
    """Converts a template object into its HOT template format.

    :param template: template object to convert
    :type  template: tuskar.templates.heat.Template

    :return: HOT template
    :rtype:  str
    """
    parameters = _compose_parameters(template)
    parameter_groups = _compose_parameter_groups(template)
    resources = _compose_resources(template)
    outputs = _compose_outputs(template)

    template_dict = {
        'heat_template_version': template.version,
        'parameters': parameters,
        'parameter_groups': parameter_groups,
        'resources': resources,
        'outputs': outputs,
    }

    # Remove optional sections if they have no values
    for x in ('parameters', 'parameter_groups', 'outputs'):
        if len(template_dict[x]) == 0:
            template_dict.pop(x)

    if template.description is not None:
        template_dict['description'] = template.description

    content = yaml.dump(template_dict, default_flow_style=False)
    return content


def compose_environment(environment):
    """Converts an environment object into its HOT template format.

    :param environment: environment object to convert
    :type  environment: tuskar.templates.heat.Environment

    :return: HOT template
    :rtype:  str
    """
    parameters = _compose_environment_parameters(environment)
    registry = _compose_resource_registry(environment)

    env_dict = {
        'parameters': parameters,
        'resource_registry': registry
    }

    content = yaml.dump(env_dict, default_flow_style=False)
    return content


def _compose_parameters(template):
    parameters = {}
    for p in template.parameters:
        details = {
            'type': p.param_type,
            'description': p.description,
            'default': p.default,
            'label': p.label,
            'hidden': p.hidden,
        }

        details = _strip_missing(details)

        if len(p.constraints) > 0:
            details['constraints'] = []

            for constraint in p.constraints:
                constraint_value = {
                    constraint.constraint_type: constraint.definition
                }
                if constraint.description is not None:
                    constraint_value['description'] = constraint.description
                details['constraints'].append(constraint_value)

        parameters[p.name] = details

    return parameters


def _compose_parameter_groups(template):
    groups = []
    for g in template.parameter_groups:
        details = {
            'label': g.label,
            'description': g.description,
            'parameters': list(g.parameter_names),  # yaml doesn't handle tuple
        }

        details = _strip_missing(details)
        if len(details['parameters']) == 0:
            details.pop('parameters')

        groups.append(details)

    return groups


def _compose_resources(template):
    resources = {}

    def _generate_details(r):
        """Converts a resource into its HOT dictionary version. This method
        will recursively call itself in the event a resource is nested within
        another as a resource definition.
        """
        d = {
            'type': r.resource_type,
            'metadata': r.metadata,
            'depends_on': r.depends_on,
            'update_policy': r.update_policy,
            'deletion_policy': r.deletion_policy,
        }

        d = _strip_missing(d)

        # Properties
        if len(r.properties) > 0:
            d['properties'] = {}
            for p in r.properties:
                if isinstance(p.value, Resource):
                    v = _generate_details(p.value)
                else:
                    v = p.value
                d['properties'][p.name] = v

        return d

    for resource in template.resources:
        details = _generate_details(resource)
        resources[resource.resource_id] = details

    return resources


def _compose_outputs(template):
    outputs = {}
    for o in template.outputs:
        details = {
            'description': o.description,
            'value': o.value,
        }

        details = _strip_missing(details)

        outputs[o.name] = details

    return outputs


def _compose_environment_parameters(environment):
    params = dict((p.name, p.value) for p in environment.parameters)
    return params


def _compose_resource_registry(environment):
    reg = dict((e.alias, e.filename) for e in environment.registry_entries)
    return reg


def _strip_missing(details):
    """Removes all entries from a dictionary whose value is None. This is used
    in this context to remove optional attributes that were added to the
    template creation.

    :type details: dict

    :return: new dictionary with the empty attributes removed
    :rtype: dict
    """
    return dict((k, v) for k, v in details.items() if v is not None)
