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

from tuskar.common import exception
from tuskar.manager.models import DeploymentPlan
from tuskar.manager.models import ParameterValue
from tuskar.manager.models import PlanParameter
from tuskar.manager.models import Role
from tuskar.manager import name_utils
from tuskar.manager.plan import MASTER_SEED_NAME
from tuskar.manager.plan import PlansManager
from tuskar.storage.exceptions import UnknownName
from tuskar.storage.exceptions import UnknownUUID
from tuskar.storage.load_roles import RESOURCE_REGISTRY_NAME
from tuskar.storage.stores import DeploymentPlanStore
from tuskar.storage.stores import EnvironmentFileStore
from tuskar.storage.stores import MasterSeedStore
from tuskar.storage.stores import MasterTemplateStore
from tuskar.storage.stores import ResourceRegistryMappingStore
from tuskar.storage.stores import ResourceRegistryStore
from tuskar.storage.stores import TemplateStore
from tuskar.templates import namespace as ns_utils
from tuskar.templates import parser
from tuskar.tests.base import TestCase


TEST_TEMPLATE = """
heat_template_version: 2013-05-23

description: Test provider resource foo

parameters:

  key_name:
    type: string
    description : Name of a KeyPair
    hidden: true
    label: Key

  instance_type:
    type: string
    description: Instance type
    default: m1.small
    constraints:
      - allowed_values: [m1.small, m1.medium, m1.large]
        description: instance_type must be one of m1.small or m1.medium

  image_id:
    type: string
    description: ID of the image to use
    default: 3e6270da-fbf7-4aef-bc78-6d0cfc3ad11b

resources:
  foo_instance:
    type: OS::Nova::Server
    properties:
      image: { get_param: image_id }
      flavor: { get_param: instance_type }
      key_name: { get_param: key_name }

outputs:
  foo_ip:
    description: IP of the created foo instance
    value: { get_attr: [foo_instance, first_address] }
"""

TEST_SEED = """
heat_template_version: 2013-05-23

description: seed template

parameters:

  role_count:
    type: number
    default: 3

  role_image:
    type: string

resources:

  my_role:
    type: OS::Heat::ResourceGroup
    properties:
      count: {get_param: role_count}
      resource_def:
        type: OS::TripleO::Role
        properties:
          image_id: {get_param: role_image}
          key_name: "hardcoded_keyname"
          instance_type: m1.large

  some_config:
    type: OS::Heat::StructuredConfig
    properties:
      config:
        ip_addresses: {get_attr: [my_role, foo_ip]}
"""

RESOURCE_REGISTRY = """
resource_registry:
  OS::TripleO::Role: r1.yaml
  OS::TripleO::Another: required_file.yaml
"""

RESOURCE_REGISTRY_WRONG_TYPE = """
resource_registry:
  OS::TripleO::UnknownRole: r1.yaml
"""


class PlansManagerTestCase(TestCase):

    def setUp(self):
        super(PlansManagerTestCase, self).setUp()
        self.plans_manager = PlansManager()

        self.plan_store = DeploymentPlanStore()
        self.template_store = TemplateStore()
        self.seed_store = MasterSeedStore()
        self.registry_store = ResourceRegistryStore()
        self.registry_mapping_store = ResourceRegistryMappingStore()

    def test_create_plan(self):
        # Tests
        created = self.plans_manager.create_plan('p1', 'desc-1')

        # Verify
        self.assertTrue(created is not None)
        self.assertTrue(isinstance(created, DeploymentPlan))
        self.assertTrue(created.uuid is not None)
        self.assertEqual('p1', created.name)
        self.assertEqual('desc-1', created.description)
        self.assertEqual(0, len(created.roles))
        self.assertEqual(0, len(created.parameters))

        found = self.plans_manager.retrieve_plan(created.uuid)
        self.assertTrue(found is not None)

    def test_delete_plan(self):
        # Setup
        created = self.plans_manager.create_plan('p1', 'desc-1')
        db_plan = self.plan_store.retrieve(created.uuid)

        # Test
        self.plans_manager.delete_plan(created.uuid)

        # Verify
        self.assertRaises(UnknownUUID,
                          self.plans_manager.retrieve_plan,
                          created.uuid)

        env_store = EnvironmentFileStore()
        self.assertRaises(UnknownUUID, env_store.retrieve,
                          db_plan.environment_file.uuid)

        master_store = MasterTemplateStore()
        self.assertRaises(UnknownUUID, master_store.retrieve,
                          db_plan.master_template.uuid)

    def test_add_role_to_plan(self):
        # Setup
        test_role = self._add_test_role()
        test_plan = self.plans_manager.create_plan('p1', 'd1')

        # Test
        self.plans_manager.add_role_to_plan(test_plan.uuid, test_role.uuid)

        # Verify
        db_plan = self.plan_store.retrieve(test_plan.uuid)
        parsed_plan = parser.parse_template(db_plan.master_template.contents)
        self.assertEqual(1, len(parsed_plan.resources))

    def test_add_role_to_seeded_plan(self):
        # Setup
        self.seed_store.create(MASTER_SEED_NAME, TEST_SEED)
        self.registry_store.create(RESOURCE_REGISTRY_NAME, RESOURCE_REGISTRY)
        # more setup (this is normally called in load_roles)
        self.registry_mapping_store.create('required_file.yaml',
                                           'some fake template data')
        test_role = self._add_test_role()
        test_plan = self.plans_manager.create_plan('p1', 'd1')

        # Test
        self.plans_manager.add_role_to_plan(test_plan.uuid, test_role.uuid)

        # Verify
        db_plan = self.plan_store.retrieve(test_plan.uuid)
        parsed_plan = parser.parse_template(db_plan.master_template.contents)
        self.assertEqual(2, len(parsed_plan.resources))

        # The role generated in the plan has a different name:
        my_role = parsed_plan.find_resource_by_id('r1-1-servers')
        self.assertIsNot(my_role, None)

        # The reference to the role in some_config should be updated:
        some_config = parsed_plan.find_resource_by_id('some_config')
        self.assertIsNot(some_config, None)
        config_property = some_config.find_property_by_name('config')
        self.assertIsNot(config_property, None)
        self.assertEqual(config_property.value,
                         {'ip_addresses':
                          {'get_attr': ['r1', 'foo_ip']}})

        # verify both entries are present from RESOURCE_REGISTRY
        parsed_env = parser.parse_environment(
            db_plan.environment_file.contents
        )
        self.assertEqual(2, len(parsed_env.registry_entries))

    def test_add_unknown_role_to_seeded_plan(self):
        # Setup
        self.seed_store.create(MASTER_SEED_NAME, TEST_SEED)
        self.registry_store.create(RESOURCE_REGISTRY_NAME, RESOURCE_REGISTRY)
        test_role = self.template_store.create('unknown_role', TEST_TEMPLATE)
        test_plan = self.plans_manager.create_plan('p1', 'd1')

        # Test
        self.assertRaises(ValueError, self.plans_manager.add_role_to_plan,
                          test_plan.uuid, test_role.uuid)

    def test_add_role_of_unknown_type_to_seeded_plan(self):
        # Setup
        self.seed_store.create(MASTER_SEED_NAME, TEST_SEED)
        self.registry_store.create(RESOURCE_REGISTRY_NAME,
                                   RESOURCE_REGISTRY_WRONG_TYPE)
        test_role = self._add_test_role()
        test_plan = self.plans_manager.create_plan('p1', 'd1')

        # Test
        self.assertRaises(ValueError, self.plans_manager.add_role_to_plan,
                          test_plan.uuid, test_role.uuid)

    def test_add_role_to_seeded_plan_without_registry(self):
        # Setup
        self.seed_store.create(MASTER_SEED_NAME, TEST_SEED)
        test_role = self._add_test_role()
        test_plan = self.plans_manager.create_plan('p1', 'd1')

        # Resource registry is missing, adding role should fail
        self.assertRaises(UnknownName,
                          self.plans_manager.add_role_to_plan,
                          test_plan.uuid, test_role.uuid)

    def test_remove_role_from_plan(self):
        # Setup
        test_role = self._add_test_role()
        test_plan = self.plans_manager.create_plan('p1', 'd1')
        self.plans_manager.add_role_to_plan(test_plan.uuid, test_role.uuid)

        # Test
        self.plans_manager.remove_role_from_plan(test_plan.uuid,
                                                 test_role.uuid)

        # Verify
        db_plan = self.plan_store.retrieve(test_plan.uuid)
        parsed_plan = parser.parse_template(db_plan.master_template.contents)
        self.assertEqual(0, len(parsed_plan.resources))

    def test_retrieve_plan(self):
        # Setup
        test_role = self._add_test_role()
        test_plan = self.plans_manager.create_plan('p1', 'd1')
        self.plans_manager.add_role_to_plan(test_plan.uuid, test_role.uuid)

        # Test
        found = self.plans_manager.retrieve_plan(test_plan.uuid)

        # Verify
        self.assertTrue(found is not None)
        self.assertTrue(isinstance(found, DeploymentPlan))
        self.assertEqual(test_plan.uuid, found.uuid)
        self.assertEqual('p1', found.name)
        self.assertEqual('d1', found.description)
        self.assertEqual(1, len(found.roles))
        self.assertTrue(isinstance(found.roles[0], Role))
        self.assertEqual(4, len(found.parameters))  # 3 + 1 for scaling
        self.assertTrue(isinstance(found.parameters[0], PlanParameter))

    def test_list_plans(self):
        # Setup
        self.plans_manager.create_plan('p1', 'd1')
        self.plans_manager.create_plan('p2', 'd2')

        # Test
        all_plans = self.plans_manager.list_plans()

        # Verify
        self.assertEqual(2, len(all_plans))
        all_plans.sort(key=lambda x: x.name)
        self.assertEqual('p1', all_plans[0].name)
        self.assertEqual('p2', all_plans[1].name)

    def test_set_parameter_values(self):
        # Setup
        test_role = self._add_test_role()
        test_plan = self.plans_manager.create_plan('p1', 'd1')
        self.plans_manager.add_role_to_plan(test_plan.uuid, test_role.uuid)

        # Test
        ns = name_utils.generate_role_namespace(test_role.name,
                                                test_role.version)
        update_us = [
            ParameterValue(ns_utils.apply_template_namespace(ns, 'key_name'),
                           'test-key'),
            ParameterValue(ns_utils.apply_template_namespace(ns, 'image_id'),
                           'test-image'),
        ]
        updated_plan = self.plans_manager.set_parameter_values(test_plan.uuid,
                                                               update_us)

        # Verify
        self.assertTrue(updated_plan is not None)
        self.assertTrue(isinstance(updated_plan, DeploymentPlan))

        # Pull it from the database again to make sure it was saved
        found = self.plans_manager.retrieve_plan(test_plan.uuid)
        found_params = sorted(found.parameters, key=lambda x: x.name)
        self.assertEqual(4, len(found_params))  # 3 + 1 for scaling
        self.assertEqual(found_params[0].value, '1')
        self.assertEqual(found_params[1].value, 'test-image')
        self.assertEqual(found_params[2].value, 'm1.small')
        self.assertEqual(found_params[3].value, 'test-key')

    def test_set_non_existent_parameters(self):
        # Setup
        test_role = self._add_test_role()
        test_plan = self.plans_manager.create_plan('p1', 'd1')
        self.plans_manager.add_role_to_plan(test_plan.uuid, test_role.uuid)

        # Test
        ns = name_utils.generate_role_namespace(test_role.name,
                                                test_role.version)
        not_present_in_role_1_name = ns_utils.apply_template_namespace(
            ns, 'not_present_in_role_1')
        not_present_in_role_2_name = ns_utils.apply_template_namespace(
            ns, 'not_present_in_role_2')
        update_us = [
            ParameterValue(ns_utils.apply_template_namespace(ns, 'key_name'),
                           'test-key'),
            ParameterValue(ns_utils.apply_template_namespace(ns, 'image_id'),
                           'test-image'),
            ParameterValue(not_present_in_role_1_name,
                           'not-present-in-role-1-value'),
            ParameterValue(not_present_in_role_2_name,
                           'not-present-in-role-2-value'),
        ]

        # Verify
        exc = self.assertRaises(exception.PlanParametersNotExist,
                                self.plans_manager.set_parameter_values,
                                test_plan.uuid,
                                update_us)
        self.assertIn(not_present_in_role_1_name, str(exc))
        self.assertIn(not_present_in_role_2_name, str(exc))

        # Pull it from the database to make sure it was modified
        found = self.plans_manager.retrieve_plan(test_plan.uuid)
        found_params = sorted(found.parameters, key=lambda x: x.name)
        self.assertEqual(4, len(found_params))  # 3 + 1 for scaling
        self.assertEqual(found_params[0].value, '1')
        self.assertEqual(found_params[1].value,
                         '3e6270da-fbf7-4aef-bc78-6d0cfc3ad11b')
        self.assertEqual(found_params[2].value, 'm1.small')
        self.assertEqual(found_params[3].value, '')

    def test_package_templates(self):
        # Setup
        test_role = self._add_test_role()
        test_plan = self.plans_manager.create_plan('p1', 'd1')
        self.plans_manager.add_role_to_plan(test_plan.uuid, test_role.uuid)

        # Test
        templates = self.plans_manager.package_templates(test_plan.uuid)

        # Verify
        self.assertTrue(isinstance(templates, dict))
        self.assertEqual(3, len(templates))

        self.assertTrue('plan.yaml' in templates)
        parsed_plan = parser.parse_template(templates['plan.yaml'])
        self.assertEqual(parsed_plan.description, 'd1')

        self.assertTrue('environment.yaml' in templates)
        parsed_env = parser.parse_environment(templates['environment.yaml'])
        self.assertEqual(1, len(parsed_env.registry_entries))

        role_filename = name_utils.role_template_filename('r1', '1', None)
        self.assertTrue(role_filename in templates)
        parsed_role = parser.parse_template(templates[role_filename])
        self.assertEqual(parsed_role.description, 'Test provider resource foo')

    def test_package_templates_seeded_plan(self):
        # Setup
        self.seed_store.create(MASTER_SEED_NAME, TEST_SEED)
        self.registry_store.create(RESOURCE_REGISTRY_NAME, RESOURCE_REGISTRY)
        # more setup (this is normally called in load_roles)
        self.registry_mapping_store.create('required_file.yaml',
                                           'some fake template data')

        test_role = self._add_test_role()
        test_plan = self.plans_manager.create_plan('p1', 'd1')
        self.plans_manager.add_role_to_plan(test_plan.uuid, test_role.uuid)

        # Test
        templates = self.plans_manager.package_templates(test_plan.uuid)

        # Verify
        self.assertTrue(isinstance(templates, dict))
        self.assertEqual(4, len(templates))

        self.assertTrue('plan.yaml' in templates)
        parsed_plan = parser.parse_template(templates['plan.yaml'])
        self.assertEqual(parsed_plan.description, 'd1')

        self.assertTrue('environment.yaml' in templates)
        self.assertTrue('required_file.yaml' in templates)
        parsed_env = parser.parse_environment(templates['environment.yaml'])
        self.assertEqual(2, len(parsed_env.registry_entries))

        role_filename = name_utils.role_template_filename('r1', '1', None)
        self.assertTrue(role_filename in templates)
        parsed_role = parser.parse_template(templates[role_filename])
        self.assertEqual(parsed_role.description, 'Test provider resource foo')

    def test_find_roles(self):
        # Setup
        self.seed_store.create(MASTER_SEED_NAME, TEST_SEED)
        self.registry_store.create(RESOURCE_REGISTRY_NAME, RESOURCE_REGISTRY)
        # more setup (this is normally called in load_roles)
        self.registry_mapping_store.create('required_file.yaml',
                                           'some fake template data')
        test_role = self._add_test_role()
        test_plan = self.plans_manager.create_plan('p1', 'd1')

        # Test
        self.plans_manager.add_role_to_plan(test_plan.uuid, test_role.uuid)

        # Verify only one role is found
        db_plan = self.plan_store.retrieve(test_plan.uuid)
        parsed_env = parser.parse_environment(
            db_plan.environment_file.contents
        )
        roles = self.plans_manager._find_roles(parsed_env)
        self.assertEqual(1, len(roles))

    def _add_test_role(self):
        return self.template_store.create('r1', TEST_TEMPLATE,
                                          registry_path='r1.yaml')
