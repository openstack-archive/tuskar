# -*- encoding: utf-8 -*-
#
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

import yaml

from tuskar.templates import composer
from tuskar.templates import heat


class ComposerTests(unittest.TestCase):

    def test_compose_template(self):
        # Test
        sample = self._sample_template()
        composed = composer.compose_template(sample)

        # Verify
        self.assertTrue(isinstance(composed, str))

        # Check that it can both be parsed back as YAML and use the resulting
        # dict in the assertions
        template = yaml.safe_load(composed)

        # Verify Overall Structure
        self.assertEqual(5, len(template))
        self.assertTrue('heat_template_version' in template)
        self.assertTrue('description' in template)
        self.assertTrue('parameters' in template)
        self.assertTrue('resources' in template)
        self.assertTrue('outputs' in template)

        # Verify Top-Level Attributes
        self.assertEqual('2013-05-23', template['heat_template_version'])
        self.assertEqual('template-desc', template['description'])

        # Verify Parameters
        self.assertEqual(2, len(template['parameters']))

        self.assertTrue('p1' in template['parameters'])
        self.assertEqual('t1', template['parameters']['p1']['type'])
        self.assertEqual('desc-1', template['parameters']['p1']['description'])
        self.assertEqual('l1', template['parameters']['p1']['label'])
        self.assertEqual('def-1', template['parameters']['p1']['default'])
        self.assertEqual(True, template['parameters']['p1']['hidden'])

        self.assertTrue('p2' in template['parameters'])
        self.assertEqual('t2', template['parameters']['p2']['type'])
        self.assertTrue('description' not in template['parameters']['p2'])
        self.assertTrue('label' not in template['parameters']['p2'])
        self.assertTrue('default' not in template['parameters']['p2'])
        self.assertTrue('hidden' not in template['parameters']['p2'])

        # Verify Resources
        self.assertEqual(2, len(template['resources']))

        self.assertTrue('r1' in template['resources'])
        self.assertEqual('t1', template['resources']['r1']['type'])
        self.assertEqual('m1', template['resources']['r1']['metadata'])
        self.assertEqual('r2', template['resources']['r1']['depends_on'])
        self.assertEqual({'u1': 'u2'},
                         template['resources']['r1']['update_policy'])
        self.assertEqual({'d1': 'd2'},
                         template['resources']['r1']['deletion_policy'])

        self.assertTrue('r2' in template['resources'])
        self.assertEqual('t2', template['resources']['r2']['type'])
        self.assertTrue('metadata' not in template['resources']['r2'])
        self.assertTrue('depends_on' not in template['resources']['r2'])
        self.assertTrue('update_policy' not in template['resources']['r2'])
        self.assertTrue('deletion_policy' not in template['resources']['r2'])

        # Verify Outputs
        self.assertEqual(2, len(template['outputs']))

        self.assertTrue('n1' in template['outputs'])
        self.assertEqual('v1', template['outputs']['n1']['value'])
        self.assertEqual('desc-1', template['outputs']['n1']['description'])

        self.assertTrue('n2' in template['outputs'])
        self.assertEqual('v2', template['outputs']['n2']['value'])
        self.assertTrue('description' not in template['outputs']['n2'])

    def test_compose_environment(self):
        # Test
        sample = self._sample_environment()
        composed = composer.compose_environment(sample)

        # Verify
        self.assertTrue(isinstance(composed, str))

        # Check that it can both be parsed back as YAML and use the resulting
        # dict in the assertions
        template = yaml.safe_load(composed)

        # Verify Overall Structure
        self.assertEqual(2, len(template))
        self.assertTrue('parameters' in template)
        self.assertTrue('resource_registry' in template)

        # Verify Parameters
        self.assertEqual(2, len(template['parameters']))

        self.assertTrue('n1' in template['parameters'])
        self.assertEqual('v1', template['parameters']['n1'])

        self.assertTrue('n2' in template['parameters'])
        self.assertEqual('v2', template['parameters']['n2'])

        # Verify Resource Registry
        self.assertEqual(2, len(template['resource_registry']))

        self.assertTrue('a1' in template['resource_registry'])
        self.assertEqual('f1', template['resource_registry']['a1'])

        self.assertTrue('a2' in template['resource_registry'])
        self.assertEqual('f2', template['resource_registry']['a2'])

    def _sample_template(self):
        t = heat.Template(description='template-desc')

        # Complex Parameter
        param = heat.Parameter('p1', 't1', description='desc-1', label='l1',
                               default='def-1', hidden=True)
        param.add_constraint(heat.ParameterConstraint('t1', 'def-1',
                                                      description='desc-1'))
        t.add_parameter(param)

        # Simple Parameter
        t.add_parameter(heat.Parameter('p2', 't2'))

        # Complex Resource
        resource = heat.Resource('r1', 't1', metadata='m1', depends_on='r2',
                                 update_policy={'u1': 'u2'},
                                 deletion_policy={'d1': 'd2'})
        t.add_resource(resource)

        # Simple Resource
        t.add_resource(heat.Resource('r2', 't2'))

        # Complex Output
        t.add_output(heat.Output('n1', 'v1', description='desc-1'))

        # Simple Output
        t.add_output(heat.Output('n2', 'v2'))

        return t

    def _sample_environment(self):
        e = heat.Environment()

        e.add_parameter(heat.EnvironmentParameter('n1', 'v1'))
        e.add_parameter(heat.EnvironmentParameter('n2', 'v2'))

        e.add_registry_entry(heat.RegistryEntry('a1', 'f1'))
        e.add_registry_entry(heat.RegistryEntry('a2', 'f2'))

        return e
