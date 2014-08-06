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
from tuskar.templates.heat import RegistryEntry
from tuskar.templates.heat import Resource
from tuskar.templates.heat import ResourceProperty
from tuskar.templates.heat import Template
import tuskar.templates.namespace as ns_utils


class DeploymentPlan(object):

    def __init__(self, master_template=None, environment=None,
                 description=None):
        super(DeploymentPlan, self).__init__()
        self.master_template = (
            master_template or Template(description=description))
        self.environment = environment or Environment()

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
        # Add Parameters
        for add_me in template.parameters:
            cloned = copy.deepcopy(add_me)
            cloned.name = ns_utils.apply_template_namespace(namespace,
                                                            add_me.name)
            self.master_template.add_parameter(cloned)

        # Create Resource
        resource = Resource(_generate_resource_id(namespace), resource_alias)
        self.master_template.add_resource(resource)

        for map_me in template.parameters:
            name = map_me.name
            master_name = ns_utils.apply_template_namespace(namespace,
                                                            map_me.name)
            value = {'get_param': [master_name]}
            resource_property = ResourceProperty(name, value)
            resource.add_property(resource_property)

        # Add Outputs
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
