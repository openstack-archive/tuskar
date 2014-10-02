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
from tuskar.templates import plan
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
  RoleParameterCount:
    type: int

  RoleParameter1:
    type: string

  RoleParameter2:
    type: string

resources:

  # Top Level Resources
  TopLevelResource1:
    type: OS::Heat::StructuredConfig
    properties:
      resource_def:
        type: OS::Heat::StructuredDeployment
        properties:
          config-1: {get_param: TopLevelParameter1}
          config-2: {get_attr: [RoleResource1, key-1]}
          config-3: {get_resource: RoleResource1}
          config-4:
            hosts:
              list_join:
              - "+"
              - - list_join:
                  - "+"
                  - {get_attr: [RoleResource1, hosts_entry]}
                - list_join:
                  - "+"
                  - {get_attr: [Controller, hosts_entry]}

  TopLevelResource2:
    type: OS::Heat::RandomString
    properties:
      config-1: {get_param: TopLevelParameter1}
      config-2: {get_attr: [RoleResourceX, key-1]}
      config-3:
        sub-1:
          sub-2: {get_param: RoleParameter1}

  # Role Resources
  RoleResource1:
    type: OS::Heat::ResourceGroup
    properties:
      count: {get_param: RoleParameterCount}
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
        self.environment = heat.Environment()

    def test_add_top_level_parameters(self):
        # Test
        template_seed.add_top_level_parameters(self.seed_template,
                                               self.destination_template,
                                               self.environment)

        # Verify
        self.assertEqual(2, len(self.destination_template.parameters))
        added_parameter_names = [p.name for p
                                 in self.destination_template.parameters]
        self.assertEqual(['TopLevelParameter1', 'TopLevelParameter2'],
                         sorted(added_parameter_names))

        added_parameter_names = [p.name for p
                                 in self.environment.parameters]
        self.assertEqual(['TopLevelParameter1', 'TopLevelParameter2'],
                         sorted(added_parameter_names))

    def test_add_top_level_parameters_idempotency(self):
        # Test
        template_seed.add_top_level_parameters(self.seed_template,
                                               self.destination_template,
                                               self.environment)
        template_seed.add_top_level_parameters(self.seed_template,
                                               self.destination_template,
                                               self.environment)

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
        mapping = template_seed.get_property_map_for_role(
            self.seed_template, 'OS::TripleO::Controller')

        # Verify
        self.assertEqual(1, len(mapping))
        self.assertTrue('RoleParameter3' in mapping)
        self.assertEqual(mapping['RoleParameter3'],
                         {'get_attr': ['TopLevelResource2', 'value']})

    def test_get_property_map_for_nonexistent_role(self):
        mapping = template_seed.get_property_map_for_role(self.seed_template,
                                                          'missing')
        self.assertTrue(mapping is None)

    def test_update_role_references(self):
        # Test
        # This will update the seed template in place. It's good enough for
        # a test as there is data within that exercises this call.
        seed_role = template_seed.find_role_from_type(
            self.seed_template.resources,
            'OS::TripleO::Controller')
        template_seed.update_role_resource_references(
            self.seed_template, seed_role, 'converted'
        )

        # Verify
        updated = self.seed_template.find_resource_by_id('TopLevelResource1')
        resource_def = updated.properties[0]
        config_props = resource_def.value['properties']
        self.assertEqual(config_props['config-1'],
                         {'get_param': 'TopLevelParameter1'})
        self.assertEqual(config_props['config-2'],
                         {'get_attr': ['converted', 'key-1']})
        self.assertEqual(config_props['config-3'],
                         {'get_resource': 'converted'})

        self.maxDiff = None
        config_4 = {
            'hosts': {
                'list_join':
                [
                    '+',
                    [
                        {'list_join': [
                            '+',
                            {'get_attr': ['converted', 'hosts_entry']}
                        ]},
                        {'list_join': [
                            '+',
                            {'get_attr': ['Controller', 'hosts_entry']}
                        ]}
                    ]
                ]
            }
        }
        self.assertEqual(config_props['config-4'], config_4)

        untouched = self.seed_template.find_resource_by_id('TopLevelResource2')
        self.assertEqual(untouched.find_property_by_name('config-1').value,
                         {'get_param': 'TopLevelParameter1'})
        self.assertEqual(untouched.find_property_by_name('config-2').value,
                         {'get_attr': ['RoleResourceX', 'key-1']})

    def test_update_role_property_references(self):
        # Setup
        dp = plan.DeploymentPlan()
        dp.add_template('ns1', self.role_template, 'foo.yaml')

        template_seed.add_top_level_resources(self.seed_template,
                                              dp.master_template)
        template_seed.add_top_level_resources(self.seed_template,
                                              dp.master_template)

        # Test
        seed_role = template_seed.find_role_from_type(
            self.seed_template.resources,
            'OS::TripleO::Controller')
        template_seed.update_role_property_references(
            dp.master_template,
            seed_role, 'ns1')

        # Verify
        tlr2 = dp.master_template.find_resource_by_id('TopLevelResource2')
        self.assertTrue(tlr2 is not None)
        c3 = tlr2.find_property_by_name('config-3')
        sub2 = c3.value['sub-1']['sub-2']
        self.assertTrue('get_param' in sub2)
        self.assertEqual('ns1::RoleParameter1', sub2['get_param'])
