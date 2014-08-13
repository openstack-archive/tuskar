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

import unittest

from tuskar.templates import heat
from tuskar.templates import namespace as ns_utils
from tuskar.templates import plan


class DeploymentPlanTests(unittest.TestCase):

    def test_empty(self):
        # Test
        p = plan.DeploymentPlan(description='test-desc')
        str(p)  # should not error

        # Verify
        self.assertTrue(isinstance(p.master_template, heat.Template))
        self.assertTrue(isinstance(p.environment, heat.Environment))
        self.assertEqual('test-desc', p.master_template.description)
        self.assertEqual(p.add_scaling, True)

    def test_existing_pieces(self):
        # Test
        t = heat.Template()
        e = heat.Environment()
        p = plan.DeploymentPlan(master_template=t, environment=e)

        # Verify
        self.assertTrue(p.master_template is t)
        self.assertTrue(p.environment is e)

    def test_add_template_no_scaling(self):
        # Test
        p = plan.DeploymentPlan(add_scaling=False)
        t = self._generate_template()
        p.add_template('ns1', t, 'template-1.yaml')

        # Verify Master Template Parameters
        self.assertEqual(2, len(p.master_template.parameters))
        for original, added in zip(t.parameters, p.master_template.parameters):
            self.assertTrue(added is not original)

            expected_name = ns_utils.apply_template_namespace('ns1',
                                                              original.name)
            self.assertEqual(added.name, expected_name)
            self.assertEqual(added.param_type, original.param_type)

        # Verify Resource
        self.assertEqual(1, len(p.master_template.resources))
        added = p.master_template.resources[0]

        expected_id = plan._generate_resource_id('ns1')
        self.assertEqual(added.resource_id, expected_id)
        expected_type = ns_utils.apply_resource_alias_namespace('ns1')
        self.assertEqual(added.resource_type, expected_type)

        for param, prop in zip(t.parameters, added.properties):
            v = ns_utils.apply_template_namespace('ns1', param.name)
            expected_value = {'get_param': [v]}
            self.assertEqual(prop.value, expected_value)

        # Verify Environment Parameters
        self.assertEqual(2, len(p.environment.parameters))
        for env_param, template_param in zip(p.environment.parameters,
                                             t.parameters):
            expected_name = (
                ns_utils.apply_template_namespace('ns1', template_param.name))
            self.assertEqual(env_param.name, expected_name)
            self.assertEqual(env_param.value, '')

        # Verify Resource Registry Entry
        self.assertEqual(1, len(p.environment.registry_entries))
        added = p.environment.registry_entries[0]
        expected_alias = ns_utils.apply_resource_alias_namespace('ns1')
        self.assertEqual(added.alias, expected_alias)
        self.assertEqual(added.filename, 'template-1.yaml')

    def test_add_template_with_default_parameter_value(self):
        # Test
        p = plan.DeploymentPlan()
        t = heat.Template()
        t.add_parameter(heat.Parameter('param-1', 'type-1', default='d1'))
        t.add_parameter(heat.Parameter('param-2', 'type-2'))
        p.add_template('ns1', t, 'template-1.yaml')

        # Verify
        p1 = p.environment.parameters[0]
        self.assertEqual(ns_utils.apply_template_namespace('ns1', 'param-1'),
                         p1.name)
        self.assertEqual('d1', p1.value)

        p2 = p.environment.parameters[1]
        self.assertEqual(ns_utils.apply_template_namespace('ns1', 'param-2'),
                         p2.name)
        self.assertEqual('', p2.value)

    def test_add_scaling_with_scaling(self):
        # Test
        p = plan.DeploymentPlan(add_scaling=True)
        t = self._generate_template()
        p.add_template('ns1', t, 'template-1.yaml')

        # Verify Master Template Count Parameters
        self.assertEqual(3, len(p.master_template.parameters))
        count_param = p.master_template.parameters[2]
        expected_count_name = plan._generate_count_property_name('ns1')
        self.assertEqual(count_param.name, expected_count_name)
        self.assertEqual(count_param.param_type, 'number')

        self.assertEqual(1, len(count_param.constraints))
        const = count_param.constraints[0]
        self.assertTrue(isinstance(const, heat.ParameterConstraint))
        self.assertEqual(const.constraint_type, 'range')
        self.assertEqual(const.definition, {'min': 1})

        # Verify Resource Group Wrapper
        self.assertEqual(1, len(p.master_template.resources))
        group_res = p.master_template.resources[0]
        group_id = plan._generate_group_id(plan._generate_resource_id('ns1'))
        self.assertEqual(group_res.resource_id, group_id)
        self.assertEqual(group_res.resource_type,
                         plan.HEAT_TYPE_RESOURCE_GROUP)

        self.assertEqual(2, len(group_res.properties))
        count_prop = group_res.properties[0]
        self.assertEqual(count_prop.name, plan.PROPERTY_SCALING_COUNT)
        self.assertEqual(count_prop.value,
                         {'get_param': [expected_count_name]})

        def_prop = group_res.properties[1]
        self.assertEqual(def_prop.name, plan.PROPERTY_RESOURCE_DEFINITION)
        self.assertTrue(isinstance(def_prop.value, heat.Resource))

        # Verify Environment Parameters
        self.assertEqual(3, len(p.environment.parameters))
        count_param = p.environment.parameters[2]
        self.assertEqual(count_param.name, expected_count_name)
        self.assertEqual(count_param.value, 1)

    def test_remove_template(self):
        # Setup & Sanity Check
        p = plan.DeploymentPlan(add_scaling=False)
        t = self._generate_template()
        p.add_template('ns1', t, 'template-1.yaml')
        p.add_template('ns2', t, 'template-2.yaml')

        self.assertEqual(4, len(p.master_template.parameters))
        self.assertEqual(4, len(p.master_template.outputs))
        self.assertEqual(2, len(p.master_template.resources))

        self.assertEqual(4, len(p.environment.parameters))
        self.assertEqual(2, len(p.environment.registry_entries))

        # Test
        p.remove_template('ns1')

        # Verify
        self.assertEqual(2, len(p.master_template.parameters))
        self.assertEqual(2, len(p.master_template.outputs))
        self.assertEqual(1, len(p.master_template.resources))

        self.assertEqual(2, len(p.environment.parameters))
        self.assertEqual(1, len(p.environment.registry_entries))

    def test_set_value(self):
        # Setup
        p = plan.DeploymentPlan()
        set_me = heat.EnvironmentParameter('p1', 'v1')
        p.environment.add_parameter(set_me)

        # Test
        p.set_value('p1', 'v2')

        # Verify
        self.assertEqual(p.environment.find_parameter_by_name('p1').value,
                         'v2')

    def test_set_value_missing_parameter(self):
        # Setup
        p = plan.DeploymentPlan()

        # Test
        self.assertRaises(ValueError, p.set_value, 'missing', 'irrelevant')

    def _generate_template(self):
        t = heat.Template()

        t.add_parameter(heat.Parameter('param-1', 'type-1'))
        t.add_parameter(heat.Parameter('param-2', 'type-2'))

        t.add_output(heat.Output('out-1', 'value-1'))
        t.add_output(heat.Output('out-2', 'value-2'))

        return t
