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
from tuskar.templates import parser
from tuskar.templates import template_seed


SEED_TEMPLATE = """
heat_template_version: 2014-10-16

description: test template

parameters:

  # Top Level Parameters
  TopLevelParameter1:
    type: string
  TopLevelParameter2:
    type: string

  # Role Parameters
  RoleParameter1:
    type: string

  RoleParameter2:
    type: string

resources:

  # Top Level Resources
  TopLevelResource1:
    type: OS::Heat::StructuredConfig

  TopLevelResource2:
    type: OS::Heat::RandomString

  # Role Resources
  RoleResource1:
    type: OS::Heat::ResourceGroup
    properties:
      count: {get_param: RoleParameter1}
      resource_def:
        type: OS::TripleO::Controller
        properties:
          RoleParameter1: {get_param: RoleParameter1}
          RoleParameter2: {get_param: RoleParameter2}
          RoleParameter3: {get_attr: [TopLevelResource2, value]}

outputs:

  Output1:
    description: output1
    value: {get_attr: [TopLevelResource2, value]}
"""

ROLE_TEMPLATE = """
heat_template_version: 2014-10-16

parameters:
  ExistingRoleParameter:
    type: string
"""


class TemplateSeedTests(unittest.TestCase):

    def setUp(self):
        super(TemplateSeedTests, self).setUp()

        self.seed_template = parser.parse_template(SEED_TEMPLATE)
        self.role_template = parser.parse_template(ROLE_TEMPLATE)
        self.destination_template = heat.Template()

    def test_add_top_level_parameters(self):
        # Test
        template_seed.add_top_level_parameters(self.seed_template,
                                               self.destination_template)

        # Verify
        self.assertEqual(2, len(self.destination_template.parameters))
        added_parameter_names = [p.name for p
                                 in self.destination_template.parameters]
        self.assertEqual(['TopLevelParameter1', 'TopLevelParameter2'],
                         sorted(added_parameter_names))

    def test_add_top_level_parameters_idempotency(self):
        # Test
        template_seed.add_top_level_parameters(self.seed_template,
                                               self.destination_template)
        template_seed.add_top_level_parameters(self.seed_template,
                                               self.destination_template)

        # Verify
        self.assertEqual(2, len(self.destination_template.parameters))

    def test_add_top_level_resources(self):
        # Test
        template_seed.add_top_level_resources(self.seed_template,
                                              self.destination_template)

        # Verify
        self.assertEqual(2, len(self.destination_template.resources))
        added_resource_ids = [r.resource_id for r
                              in self.destination_template.resources]
        self.assertEqual(['TopLevelResource1', 'TopLevelResource2'],
                         sorted(added_resource_ids))

    def test_add_top_level_resources_idempotency(self):
        # Test
        template_seed.add_top_level_resources(self.seed_template,
                                              self.destination_template)
        template_seed.add_top_level_resources(self.seed_template,
                                              self.destination_template)

        # Verify
        self.assertEqual(2, len(self.destination_template.resources))

    def test_add_top_level_outputs(self):
        # Test
        template_seed.add_top_level_outputs(self.seed_template,
                                            self.destination_template)

        # Verify
        self.assertEqual(1, len(self.destination_template.outputs))
        self.assertEqual('Output1', self.destination_template.outputs[0].name)

    def test_add_top_level_outputs_idempotency(self):
        # Test
        template_seed.add_top_level_outputs(self.seed_template,
                                            self.destination_template)
        template_seed.add_top_level_outputs(self.seed_template,
                                            self.destination_template)

        # Verify
        self.assertEqual(1, len(self.destination_template.outputs))

    def test_get_property_map_for_role(self):
        # Test
        mapping = template_seed.get_property_map_for_role(self.seed_template,
                                                          'RoleResource1')

        # Verify
        self.assertEqual(1, len(mapping))
        self.assertTrue('RoleParameter3' in mapping)
        self.assertEqual(mapping['RoleParameter3'],
                         {'get_attr': ['TopLevelResource2', 'value']})

    def test_get_property_map_for_nonexistent_role(self):
        self.assertRaises(ValueError, template_seed.get_property_map_for_role,
                          self.seed_template, 'missing')
