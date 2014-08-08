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
Object representations of the elements of a HOT template.

These objects were created against the HOT specification found at:
http://docs.openstack.org/developer/heat/template_guide/hot_spec.html
"""

from tuskar.templates import namespace as ns_utils


DEFAULT_VERSION = '2013-05-23'


class Template(object):

    def __init__(self, version=DEFAULT_VERSION, description=None):
        super(Template, self).__init__()
        self.version = version
        self.description = description
        self._parameter_groups = []  # list of ParameterGroup
        self._parameters = []  # list of Parameter
        self._resources = []  # list of Resource
        self._outputs = []  # list of Output

    def __str__(self):
        msg = ('Template: version=%(ver)s, description=%(desc)s, '
               'parameter_count=%(param)s, output_count=%(out)s')
        data = {
            'ver': self.version,
            'desc': _safe_strip(self.description),
            'param': len(self.parameters),
            'out': len(self.outputs)
        }

        return msg % data

    @property
    def parameter_groups(self):
        return tuple(self._parameter_groups)

    @property
    def parameters(self):
        return tuple(self._parameters)

    @property
    def resources(self):
        return tuple(self._resources)

    @property
    def outputs(self):
        return tuple(self._outputs)

    def add_parameter(self, parameter):
        """Adds a parameter to the template.

        :type parameter: tuskar.templates.heat.Parameter
        """
        self._parameters.append(parameter)

    def remove_parameter(self, parameter):
        """Removes a parameter from the template.

        :type parameter: tuskar.templates.heat.Parameter
        :raise ValueError: if the parameter is not in the template
        """
        self._parameters.remove(parameter)

    def remove_parameters_by_namespace(self, namespace):
        """Removes all parameters in the given namespace.

        :type namespace: str
        """
        self._parameters = [
            p for p in self.parameters
            if not ns_utils.matches_template_namespace(namespace, p.name)]

    def add_parameter_group(self, parameter_group):
        """Adds a parameter group to the template.

        :type parameter_group: tuskar.templates.heat.ParameterGroup
        """
        self._parameter_groups.append(parameter_group)

    def remove_parameter_group(self, parameter_group):
        """Removes a parameter group from the template.

        :type parameter_group: tuskar.templates.heat.ParameterGroup
        :raise ValueError: if the parameter group is not in the template
        """
        self._parameter_groups.remove(parameter_group)

    def add_resource(self, resource):
        """Adds a resource to the template.

        :type resource: tuskar.templates.heat.Resource
        """
        self._resources.append(resource)

    def remove_resource(self, resource):
        """Removes a resource from the template.

        :type resource: tuskar.templates.heat.Resource
        :raise ValueError: if the resource is not in the template
        """
        self._resources.remove(resource)

    def remove_resource_by_id(self, resource_id):
        """Removes a resource from the template if found.

        :type resource_id: str
        """
        self._resources = [r for r in self._resources
                           if r.resource_id != resource_id]

    def add_output(self, output):
        """Adds an output to the template.

        :type output: tuskar.templates.heat.Output
        """
        self._outputs.append(output)

    def remove_output(self, output):
        """Removes an output from the template.

        :type output: tuskar.templates.heat.Output
        :raise ValueError: if the output is not in the template
        """
        self._outputs.remove(output)

    def remove_outputs_by_namespace(self, namespace):
        """Removes all outputs in the given namespace from the template.

        :type namespace: str
        """
        self._outputs = [
            o for o in self.outputs
            if not ns_utils.matches_template_namespace(namespace, o.name)]


class ParameterGroup(object):

    def __init__(self, label, description=None):
        super(ParameterGroup, self).__init__()
        self.label = label
        self.description = description
        self._parameter_names = set()

    def __str__(self):
        msg = ('ParameterGroup: label=%(label)s, description=%(desc)s '
               'parameter_names=%(names)s')
        data = {
            'label': self.label,
            'desc': self.description,
            'names': ','.join(self.parameter_names),
        }
        return msg % data

    @property
    def parameter_names(self):
        return tuple(self._parameter_names)

    def add_parameter_name(self, *names):
        """Adds one or more parameters to the group.

        :type names: str
        """
        for n in names:
            self._parameter_names.add(n)

    def remove_parameter_name(self, name):
        """Removes a parameter from the group if it is present.

        :type name: str
        """
        self._parameter_names.discard(name)


class Parameter(object):

    def __init__(self, name, param_type,
                 description=None, label=None, default=None, hidden=None):
        super(Parameter, self).__init__()
        self.name = name
        self.param_type = param_type
        self.description = description
        self.label = label
        self.default = default
        self.hidden = hidden
        self._constraints = []

    def __str__(self):
        msg = ('Parameter: name=%(name)s, type=%(type)s, '
               'description=%(desc)s, label=%(label)s, '
               'default=%(def)s, hidden=%(hidden)s')
        data = {
            'name': self.name,
            'type': self.param_type,
            'desc': self.description,
            'label': self.label,
            'def': self.default,
            'hidden': self.hidden,
        }
        return msg % data

    @property
    def constraints(self):
        return tuple(self._constraints)

    def add_constraint(self, constraint):
        """Adds a constraint to the parameter.

        :type constraint: tuskar.templates.heat.ParameterConstraint
        """
        self._constraints.append(constraint)

    def remove_constraint(self, constraint):
        """Removes a constraint from the template.

        :type constraint: tuskar.templates.heat.ParameterConstraint
        :raise ValueError: if the given constraint isn't in the parameter
        """
        self._constraints.remove(constraint)


class ParameterConstraint(object):

    def __init__(self, constraint_type, definition, description=None):
        super(ParameterConstraint, self).__init__()
        self.constraint_type = constraint_type
        self.definition = definition
        self.description = description

    def __str__(self):
        msg = ('Constraint: type=%(type)s, definition=%(def)s, '
               'description=%(desc)s')
        data = {
            'type': self.constraint_type,
            'def': self.definition,
            'desc': self.description,
        }
        return msg % data


class Resource(object):

    def __init__(self, resource_id, resource_type,
                 metadata=None, depends_on=None,
                 update_policy=None, deletion_policy=None):
        super(Resource, self).__init__()
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.metadata = metadata
        self.depends_on = depends_on
        self.update_policy = update_policy
        self.deletion_policy = deletion_policy
        self._properties = []

    def __str__(self):
        msg = 'Resource: id=%(id)s, resource_type=%(type)s'
        data = {
            'id': self.resource_id,
            'type': self.resource_type,
        }
        return msg % data

    @property
    def properties(self):
        return tuple(self._properties)

    def add_property(self, resource_property):
        """Adds a property to the resource.

        :type resource_property: tuskar.templates.heat.ResourceProperty
        """
        self._properties.append(resource_property)

    def remove_property(self, resource_property):
        """Removes a property from the template.

        :type resource_property: tuskar.templates.heat.ResourceProperty
        :raise ValueError: if the property isn't in the resource
        """
        self._properties.remove(resource_property)


class ResourceProperty(object):

    def __init__(self, name, value):
        super(ResourceProperty, self).__init__()
        self.name = name
        self.value = value

    def __str__(self):
        msg = 'ResourceProperty: name=%(name)s, value=%(value)s'
        data = {
            'name': self.name,
            'value': self.value,
        }
        return msg % data


class Output(object):

    def __init__(self, name, value, description=None):
        super(Output, self).__init__()
        self.name = name
        self.value = value
        self.description = description

    def __str__(self):
        msg = 'Output: name=%(name)s, value=%(value)s, description=%(desc)s'
        data = {
            'name': self.name,
            'value': self.value,
            'desc': _safe_strip(self.description)
        }
        return msg % data


class Environment(object):

    def __init__(self):
        super(Environment, self).__init__()
        self._parameters = []
        self._registry_entries = []

    def __str__(self):
        msg = ('Environment: parameter_count=%(p_count)s, '
               'registry_count=%(r_count)s')
        data = {
            'p_count': len(self.parameters),
            'r_count': len(self.registry_entries),
        }
        return msg % data

    @property
    def parameters(self):
        return tuple(self._parameters)

    @property
    def registry_entries(self):
        return tuple(self._registry_entries)

    def add_parameter(self, parameter):
        """Adds a property to the environment.

        :type parameter: tuskar.templates.heat.EnvironmentParameter
        """
        self._parameters.append(parameter)

    def remove_parameter(self, parameter):
        """Removes a parameter from the environment.

        :type parameter: tuskar.templates.heat.EnvironmentParameter
        :raise ValueError: if the parameter is not in the environment
        """
        self._parameters.remove(parameter)

    def remove_parameters_by_namespace(self, namespace):
        """Removes all parameters that match the given namespace.

        :type namespace: str
        """
        self._parameters = [
            p for p in self._parameters
            if not ns_utils.matches_template_namespace(namespace, p.name)]

    def find_parameter_by_name(self, name):
        """Returns the parameter instance with the given name.

        :type name: str
        :rtype: tuskar.templates.heat.EnvironmentParameter
        :raise ValueError: if there is no parameter with the given name
        """
        matching = [p for p in self._parameters if p.name == name]
        if len(matching) == 0:
            raise ValueError('No parameter named %s found' % name)
        return matching[0]

    def add_registry_entry(self, entry):
        """Adds a registry entry to the environment.

        :type entry: tuskar.templates.heat.RegistryEntry
        """
        self._registry_entries.append(entry)

    def remove_registry_entry(self, entry):
        """Removes a registry entry from the environment.

        :type entry: tuskar.templates.heat.RegistryEntry
        :raise ValueError: if the entry is not in the environment
        """
        self._registry_entries.remove(entry)

    def remove_registry_entry_by_alias(self, alias):
        """Removes a registry entry from the environment if it is found.

        :type alias: str
        """
        self._registry_entries = [e for e in self._registry_entries
                                  if e.alias != alias]


class EnvironmentParameter(object):

    def __init__(self, name, value):
        super(EnvironmentParameter, self).__init__()
        self.name = name
        self.value = value

    def __str__(self):
        msg = 'EnvironmentParameter: name=%(name)s, value=%(value)s'
        data = {
            'name': self.name,
            'value': self.value,
        }
        return msg % data


class RegistryEntry(object):

    def __init__(self, alias, filename):
        super(RegistryEntry, self).__init__()
        self.alias = alias
        self.filename = filename

    def __str__(self):
        msg = 'RegistryEntry: alias=%(alias)s, filename=%(f)s'
        data = {
            'alias': self.alias,
            'f': self.filename,
        }
        return msg % data


def _safe_strip(value):
    """Strips the value if it is not None.

    :param value: text to be cleaned up
    :type  value: str or None

    :return: clean value if one was specified; None otherwise
    :rtype: str or None
    """
    if value is not None:
        return value.strip()
    return None
