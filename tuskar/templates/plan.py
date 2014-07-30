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
Object representations of the Tuskar-specific domain concepts. These objects
are used to build up a deployment plan by adding templates (roles, in
Tuskar terminology). The composer module can then be used to translate
these models into the corresponding Heat format.
"""

import copy

from tuskar.templates.heat import Environment
from tuskar.templates.heat import EnvironmentParameter
from tuskar.templates.heat import Output
from tuskar.templates.heat import Parameter
from tuskar.templates.heat import ParameterConstraint
from tuskar.templates.heat import RegistryEntry
from tuskar.templates.heat import Resource
from tuskar.templates.heat import ResourceProperty
from tuskar.templates.heat import Template
import tuskar.templates.namespace as ns_utils


# Type string for a Heat resource group
HEAT_TYPE_RESOURCE_GROUP = 'OS::Heat::ResourceGroup'

# Name of the propety added to a resource group to control its scaling
PROPERTY_SCALING_COUNT = 'count'

# Name of the property added to a resource group to define the resources
# in the group
PROPERTY_RESOURCE_DEFINITION = 'resource_def'


class DeploymentPlan(object):

    def __init__(self, master_template=None, environment=None,
                 description=None, add_scaling=True):
        """Creates a new deployment plan. The plan can be initialized from
        an existing plan's components by passing in the master template
        and environment. Keep in mind that there are relationships between
        the master template and the environment and they should either both
        be specified or neither. If they are unspecified, empty versions of
        both files will be created.

        The add_scaling flag controls whether or not the plan will
        automatically add in Heat constructs to support scaling when a
        template is added.

        :param master_template: template instance to use for the plan
        :type  master_template: tuskar.templates.heat.Template
        :param environment: environment to use for the plan
        :type  environment: tuskar.templates.heat.Environment
        :param description: optional description for the plan's master
               template; only used if a master template is not specified
        :type  description: str
        :param add_scaling: flag controlling if the plan will automatically
               include scaling components to the master template
        :type  add_scaling: bool
        """
        super(DeploymentPlan, self).__init__()
        self.master_template = (
            master_template or Template(description=description))
        self.environment = environment or Environment()
        self.add_scaling = add_scaling

    def add_template(self, namespace, template, filename):
        """Adds a new template to the plan. The pieces of the template will
        be prefixed with the given namespace in the plan's master template.

        :param namespace: prefix to use to prevent parameter and output
                          naming conflicts
        :type  namespace: str
        :param template: template being added to the plan
        :type  template: tuskar.templates.heat.Template
        :param filename: name of the file where the template is stored, used
                         when mapping the template in the environment
        :type  filename: str
        """
        resource_alias = ns_utils.apply_resource_alias_namespace(namespace)

        self._add_to_master_template(namespace, template, resource_alias)
        self._add_to_environment(namespace, template, filename, resource_alias)

    def remove_template(self, namespace):
        """Removes all references to the template added under the given
        namespace. This call does not error if a template with the given
        namespace hasn't been added.

        :type namespace: str
        """
        self._remove_from_master_template(namespace)
        self._remove_from_environment(namespace)

    def set_value(self, name, value):
        """Sets the value for the attribute with the given name. The name
        must correspond exactly with an attribute of the plan itself; in
        other words, the namespace of the template from which the attribute
        originally came from should already be applied.

        :type name: str
        :type value: str
        :raise ValueError: if there is no parameter with the given name
        """
        p = self.environment.find_parameter_by_name(name)
        p.value = value

    def _add_to_master_template(self, namespace, template, resource_alias):
        resource = self._add_resource(namespace, template, resource_alias)
        self._add_parameters(namespace, template)
        self._add_outputs(namespace, template, resource)

    def _add_resource(self, namespace, template, resource_alias):
        resource = Resource(_generate_resource_id(namespace), resource_alias)

        for map_me in template.parameters:
            name = map_me.name
            master_name = ns_utils.apply_template_namespace(namespace,
                                                            map_me.name)
            value = {'get_param': [master_name]}
            resource_property = ResourceProperty(name, value)
            resource.add_property(resource_property)

        # If scaling features are being automatically added in, wrap the
        # resource in a resource group. The _add_parameters call will add
        # a corresponding parameter for the count of this resource.
        if self.add_scaling:
            group_resource_id = _generate_group_id(resource.resource_id)
            heat_group = Resource(group_resource_id, HEAT_TYPE_RESOURCE_GROUP)

            count_prop = ResourceProperty(
                PROPERTY_SCALING_COUNT,
                {'get_param': [_generate_count_property_name(namespace)]})
            heat_group.add_property(count_prop)

            def_prop = ResourceProperty(PROPERTY_RESOURCE_DEFINITION, resource)
            heat_group.add_property(def_prop)

            outer_resource = heat_group
        else:
            outer_resource = resource

        self.master_template.add_resource(outer_resource)
        return outer_resource

    def _add_parameters(self, namespace, template):
        for add_me in template.parameters:
            cloned = copy.deepcopy(add_me)
            cloned.name = ns_utils.apply_template_namespace(namespace,
                                                            add_me.name)
            self.master_template.add_parameter(cloned)

        # If scaling features are being automatically added in, create the
        # template parameter for accepting the count for the resource with
        # this namespace
        if self.add_scaling:
            count_param = Parameter(_generate_count_property_name(namespace),
                                    'number')
            constraint = ParameterConstraint('range', {'min': 1})
            count_param.add_constraint(constraint)
            self.master_template.add_parameter(count_param)

    def _add_outputs(self, namespace, template, resource):
        for add_me in template.outputs:
            # The output creation is a bit trickier than simply copying the
            # original. The master output is namespaced like the other pieces,
            # and it's value is retrieved from the resource that's created in
            # the master template, but will be present in that resource
            # under it's original name.
            output_name = ns_utils.apply_template_namespace(namespace,
                                                            add_me.name)
            output_value = {'get_attr': [resource.resource_id, add_me.name]}
            master_out = Output(output_name, output_value)
            self.master_template.add_output(master_out)

    def _add_to_environment(self, namespace, template,
                            filename, resource_alias):
        # Add Parameters
        for add_me in template.parameters:
            name = ns_utils.apply_template_namespace(namespace, add_me.name)
            env_parameter = EnvironmentParameter(name, add_me.default or '')
            self.environment.add_parameter(env_parameter)

        if self.add_scaling:
            count_param_name = _generate_count_property_name(namespace)
            count_param = EnvironmentParameter(count_param_name, 1)
            self.environment.add_parameter(count_param)

        # Add Resource Registry Entry
        registry_entry = RegistryEntry(resource_alias, filename)
        self.environment.add_registry_entry(registry_entry)

    def _remove_from_master_template(self, namespace):
        # Remove Parameters
        self.master_template.remove_parameters_by_namespace(namespace)

        # Remove Outputs
        self.master_template.remove_outputs_by_namespace(namespace)

        # Remove Resource
        resource_id = _generate_resource_id(namespace)
        self.master_template.remove_resource_by_id(resource_id)

    def _remove_from_environment(self, namespace):
        # Remove Parameters
        self.environment.remove_parameters_by_namespace(namespace)

        # Remove Resource Registry Entry
        resource_alias = ns_utils.apply_resource_alias_namespace(namespace)
        self.environment.remove_registry_entry_by_alias(resource_alias)


def _generate_resource_id(namespace):
    """Generates the ID of the resource to be added to the plan's master
    template when a new template is added.

    :type namespace: str
    :rtype: str
    """
    return namespace + '-resource'


def _generate_group_id(resource_id):
    """Generates the ID for a resource group wrapper resource around the
    given resource.

    :type resource_id: str
    :rtype: str
    """
    return resource_id + '-servers'


def _generate_count_property_name(namespace):
    """Generates the name of the property to hold the count of a particular
    resource as identified by its namespace. The count property will be
    prefixed by the namespace in the same way as other parameters for the
    resource.

    :type namespace: str
    :rtype: str
    """
    return ns_utils.apply_template_namespace(namespace, 'count')
