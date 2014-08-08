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

from tuskar.manager.models import DeploymentPlan
from tuskar.manager.models import PlanParameter
from tuskar.manager.models import Role
from tuskar.manager.plan import PlansManager
from tuskar.storage.exceptions import UnknownUUID
from tuskar.storage.stores import DeploymentPlanStore
from tuskar.storage.stores import EnvironmentFileStore
from tuskar.storage.stores import MasterTemplateStore
from tuskar.storage.stores import TemplateStore
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


class PlansManagerTestCase(TestCase):

    def setUp(self):
        super(PlansManagerTestCase, self).setUp()
        self.plans_manager = PlansManager()

        self.plan_store = DeploymentPlanStore()
        self.template_store = TemplateStore()

    def test_create_plan(self):
        # Test
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
        self.assertEqual(3, len(found.parameters))
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

    def _add_test_role(self):
        return self.template_store.create('r1', TEST_TEMPLATE)
