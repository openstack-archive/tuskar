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
Functionality for parsing Heat files (templates and environment files) into
their object model representations.

The parsing was written against the HOT specification found at:
http://docs.openstack.org/developer/heat/template_guide/hot_spec.html
"""

import yaml

from tuskar.templates.heat import Environment
from tuskar.templates.heat import EnvironmentParameter
from tuskar.templates.heat import Output
from tuskar.templates.heat import Parameter
from tuskar.templates.heat import ParameterConstraint
from tuskar.templates.heat import ParameterGroup
from tuskar.templates.heat import RegistryEntry
from tuskar.templates.heat import Resource
from tuskar.templates.heat import ResourceProperty
from tuskar.templates.heat import Template


def parse_template(content):
    """Parses a Heat template into the Tuskar object model.

    :param content: string representation of the template
    :type  content: str

    :return: Tuskar representation of the template
    :rtype:  tuskar.templates.heat.Template
    """
    yaml_parsed = yaml.load(content)
    template = Template()

    _parse_version(template, yaml_parsed)
    _parse_description(template, yaml_parsed)
    _parse_template_parameters(template, yaml_parsed)
    _parse_parameter_group(template, yaml_parsed)
    _parse_resources(template, yaml_parsed)
    _parse_outputs(template, yaml_parsed)

    return template


def parse_environment(content):
    """Parses a Heat environment file into the Tuskar object model.

    :param content: string representation of the environment file
    :type  content: str

    :return: Tuskar representation of the environment file
    :rtype:  tuskar.templates.heat.Environment
    """
    yaml_parsed = yaml.load(content)
    environment = Environment()

    _parse_environment_parameters(environment, yaml_parsed)
    _parse_resource_registry(environment, yaml_parsed)

    return environment


def _parse_version(template, yaml_parsed):
    template.version = (
        yaml_parsed.get('heat_template_version', None) or template.version)


def _parse_description(template, yaml_parsed):
    template.description = (
        yaml_parsed.get('description', None) or template.description)


def _parse_template_parameters(template, yaml_parsed):
    yaml_parameters = yaml_parsed.get('parameters', {})
    for name, details in yaml_parameters.items():

        # Basic parameter data
        param_type = details['type']  # required
        description = details.get('description', None)
        label = details.get('label', None)
        default = details.get('default', None)
        hidden = details.get('hidden', None)

        parameter = Parameter(name, param_type, description=description,
                              label=label, default=default, hidden=hidden)
        template.add_parameter(parameter)

        # Parse constraints if present
        constraints = details.get('constraints', None)
        if constraints is not None:
            for constraint_details in constraints:

                # The type of constraint is a key in the constraint data, so
                # rather than know all of the possible values, pop out the
                # description (if present) and assume the remaining key/value
                # pair is the type and definition.

                description = constraint_details.pop('description', None)
                constraint_type = constraint_details.keys()[0]
                definition = constraint_details[constraint_type]

                constraint = ParameterConstraint(constraint_type, definition,
                                                 description=description)
                parameter.add_constraint(constraint)


def _parse_parameter_group(template, yaml_parsed):
    yaml_groups = yaml_parsed.get('parameter_groups', [])

    for details in yaml_groups:
        label = details['label']
        description = details.get('description', None)
        param_names = details['parameters']

        group = ParameterGroup(label, description)
        group.add_parameter_name(*param_names)
        template.add_parameter_group(group)


def _parse_resources(template, yaml_parsed):
    yaml_resources = yaml_parsed.get('resources', {})
    for resource_id, details in yaml_resources.items():
        resource_type = details['type']  # required
        metadata = details.get('metadata', None)
        depends_on = details.get('depends_on', None)
        update_policy = details.get('update_policy', None)
        deletion_policy = details.get('deletion_policy', None)

        resource = Resource(resource_id, resource_type, metadata=metadata,
                            depends_on=depends_on, update_policy=update_policy,
                            deletion_policy=deletion_policy)
        template.add_resource(resource)

        for key, value in details.get('properties', {}).items():
            prop = ResourceProperty(key, value)
            resource.add_property(prop)


def _parse_outputs(template, yaml_parsed):
    yaml_outputs = yaml_parsed.get('outputs', {})
    for name, details in yaml_outputs.items():
        value = details['value']  # required

        # HOT spec doesn't list this as optional, but most descriptions are,
        # so assume it is here too
        description = details.get('description', None)

        output = Output(name, value, description=description)
        template.add_output(output)


def _parse_environment_parameters(environment, yaml_parsed):
    yaml_parameters = yaml_parsed.get('parameters', {})
    for name, value in yaml_parameters.items():
        parameter = EnvironmentParameter(name, value)
        environment.add_parameter(parameter)


def _parse_resource_registry(environment, yaml_parsed):
    yaml_entries = yaml_parsed.get('resource_registry', {})
    for namespace, filename in yaml_entries.items():
        entry = RegistryEntry(namespace, filename)
        environment.add_registry_entry(entry)
