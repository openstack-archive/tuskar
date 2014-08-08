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

import mock

from tuskar.manager.models import Role
from tuskar.manager.role import RoleManager
from tuskar.storage.exceptions import UnknownUUID
from tuskar.storage.stores import TemplateStore
from tuskar.tests.base import TestCase


TEST_TEMPLATE = """
heat_template_version: 2013-05-23
parameters: {}
resources: {}
outputs: {}
"""


class RoleManagerTests(TestCase):

    def setUp(self):
        super(RoleManagerTests, self).setUp()
        self.role_manager = RoleManager()

        self.template_store = TemplateStore()

    def test_list_roles(self):
        # Test
        self._populate_roles()
        all_roles = self.role_manager.list_roles()

        # Verify
        self.assertEqual(3, len(all_roles))
        self.assertTrue(isinstance(all_roles[0], Role))
        all_roles.sort(key=lambda x: '%s-%s' % (x.name, x.version))

        self.assertEqual('r1', all_roles[0].name)
        self.assertEqual(1, all_roles[0].version)

        self.assertEqual('r1', all_roles[1].name)
        self.assertEqual(2, all_roles[1].version)

        self.assertEqual('r2', all_roles[2].name)
        self.assertEqual(1, all_roles[2].version)

    def test_list_roles_only_latest(self):
        # Setup
        list_mock = mock.MagicMock()
        self.role_manager.template_store.list = list_mock
        list_mock.return_value = []

        # Test
        self.role_manager.list_roles(only_latest=True)

        # Verify
        list_mock.assert_called_once_with(only_latest=True)

    def test_retrieve_role_by_uuid(self):
        # Test
        added_roles = self._populate_roles()
        found = self.role_manager.retrieve_role_by_uuid(added_roles[0].uuid)

        # Verify
        self.assertTrue(found is not None)
        self.assertTrue(isinstance(found, Role))
        self.assertEqual(found.name, 'r1')
        self.assertEqual(found.version, 2)

    def test_retrieve_role_by_fake_uuid(self):
        self.assertRaises(UnknownUUID,
                          self.role_manager.retrieve_role_by_uuid,
                          'fake')

    def _populate_roles(self):
        r1 = self.template_store.create('r1', TEST_TEMPLATE)
        r1 = self.template_store.update(r1.uuid, TEST_TEMPLATE)
        r2 = self.template_store.create('r2', TEST_TEMPLATE)
        return [r1, r2]
