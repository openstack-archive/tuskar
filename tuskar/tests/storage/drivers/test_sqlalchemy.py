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

from functools import partial

from mock import patch

from tuskar.common import context as tuskar_context
from tuskar.storage.drivers.sqlalchemy import SQLAlchemyDriver
from tuskar.storage.exceptions import UnknownName
from tuskar.storage.exceptions import UnknownUUID
from tuskar.storage.exceptions import UnknownVersion
from tuskar.storage.stores import DeploymentPlanStore
from tuskar.storage.stores import TemplateStore
from tuskar.tests import base


class SQLAlchemyDriverTestCase(base.TestCase):

    def setUp(self):
        super(SQLAlchemyDriverTestCase, self).setUp()

        self.context = tuskar_context.get_admin_context()
        self.driver = SQLAlchemyDriver()
        self.store = TemplateStore(self.driver)

    @patch('tuskar.storage.drivers.sqlalchemy.SQLAlchemyDriver._generate_uuid')
    def test_create(self, mock_uuid):

        # Setup
        expected_uuid = 'b4b85dc2-0b0a-48ed-a56c-e4d582fd1473'
        mock_uuid.return_value = expected_uuid

        # Test
        result = self.driver.create(self.store, "swift.yaml", "YAML")

        # Verify
        self.assertEqual(result.uuid, expected_uuid)
        self.assertEqual(result.version, 1)

    @patch('tuskar.storage.drivers.sqlalchemy.SQLAlchemyDriver._generate_uuid')
    def test_create_no_versioning(self, mock_uuid):

        # Setup
        store = DeploymentPlanStore(self.driver)
        expected_uuid = 'b4b85dc2-0b0a-48ed-a56c-e4d582fd1473'
        mock_uuid.return_value = expected_uuid

        # Test
        result = self.driver.create(store, "swift.yaml", "YAML")

        # Verify
        self.assertEqual(result.uuid, expected_uuid)
        self.assertEqual(result.version, None)

    @patch('tuskar.storage.drivers.sqlalchemy.SQLAlchemyDriver._generate_uuid')
    def test_retrieve(self, mock_uuid):

        # Setup
        expected_uuid = 'b4b85dc2-0b0a-48ed-a56c-e4d582fd1473'
        expected_name = "swift.yaml"
        expected_contents = "YAML"
        mock_uuid.return_value = expected_uuid
        self.driver.create(self.store, expected_name, expected_contents)

        # Test
        result = self.driver.retrieve(self.store, expected_uuid)

        # Verify
        self.assertEqual(result.uuid, expected_uuid)
        self.assertEqual(result.name, expected_name)
        self.assertEqual(result.contents, expected_contents)

    def test_retrieve_invalid(self):

        # Setup
        retrieve_call = partial(
            self.driver.retrieve,
            self.store, "uuid"
        )

        # Test & Verify
        self.assertRaises(UnknownUUID, retrieve_call)

    def test_update(self):

        # Setup
        expected_name = "swift.yaml"
        original_contents = "YAML"
        created = self.driver.create(
            self.store, expected_name, original_contents)

        # Test
        new_contents = "YAML2"
        updated = self.driver.update(self.store, created.uuid, new_contents)

        # Verify
        retrieved = self.driver.retrieve(self.store, created.uuid)
        self.assertEqual(retrieved.uuid, created.uuid)
        self.assertEqual(retrieved.name, expected_name)

        # Original and retrieved have not been updated
        self.assertEqual(retrieved.contents, original_contents)
        self.assertEqual(created.version, 1)
        self.assertEqual(retrieved.version, 1)

        # Updated has a new version, and new contents
        self.assertEqual(updated.contents, new_contents)
        self.assertEqual(updated.version, 2)

    def test_update_no_versioning(self):

        # Setup
        store = DeploymentPlanStore(self.driver)
        expected_name = "swift.yaml"
        original_contents = "YAML"
        created = self.driver.create(store, expected_name, original_contents)

        # Test
        new_contents = "YAML2"
        updated = self.driver.update(store, created.uuid, new_contents)

        # Verify
        self.assertEqual(updated.uuid, created.uuid)
        self.assertEqual(updated.name, expected_name)
        self.assertEqual("YAML2", updated.contents)
        self.assertEqual(updated.version, None)

    def test_update_invalid_uuid(self):

        # Setup
        update_call = partial(self.driver.update, self.store, "uuid", "YAML2")

        # Test & Verify
        self.assertRaises(UnknownUUID, update_call)

    @patch('tuskar.storage.drivers.sqlalchemy.SQLAlchemyDriver._generate_uuid')
    def test_delete(self, mock_uuid):

        # Setup
        expected_uuid = 'b4b85dc2-0b0a-48ed-a56c-e4d582fd1473'
        expected_name = "swift.yaml"
        contents = "YAML"
        mock_uuid.return_value = expected_uuid
        self.driver.create(self.store, expected_name, contents)

        # Test
        result = self.driver.delete(self.store, expected_uuid)

        # Verify
        self.assertEqual(None, result)
        retrieve_call = partial(
            self.driver.retrieve,
            self.store, expected_uuid
        )
        self.assertRaises(UnknownUUID, retrieve_call)

    def test_delete_invalid(self):
        self.assertRaises(
            UnknownUUID, self.driver.delete, self.store, "uuid")

    def test_list(self):

        name = "swift.yaml"
        template = self.driver.create(self.store, name, "YAML1")

        self.assertEqual(1, len(self.driver.list(self.store)))

        self.driver.update(self.store, template.uuid, "YAML2")

        self.assertEqual(2, len(self.driver.list(self.store)))

    def test_list_only_latest(self):

        name = "swift.yaml"
        template = self.driver.create(self.store, name, "YAML1")
        self.driver.update(self.store, template.uuid, "YAML2")

        listed = self.driver.list(self.store, only_latest=True)

        self.assertEqual(1, len(listed))

    def test_retrieve_by_name(self):

        # Setup
        create_result = self.driver.create(self.store, "name", "YAML")
        self.driver.update(self.store, create_result.uuid, "YAML2")

        # Test
        retrieved = self.driver.retrieve_by_name(self.store, "name")

        # Verify
        self.assertNotEqual(create_result.uuid, retrieved.uuid)
        self.assertEqual(retrieved.contents, "YAML2")
        self.assertEqual(retrieved.version, 2)

    def test_retrieve_by_name_version(self):

        name = "swift.yaml"

        # Setup
        first = self.driver.create(self.store, name, "YAML1")
        second = self.driver.update(self.store, first.uuid, "YAML2")
        third = self.driver.update(self.store, first.uuid, "YAML3")

        # Test
        retrieved_first = self.driver.retrieve_by_name(self.store, name, 1)
        retrieved_second = self.driver.retrieve_by_name(self.store, name, 2)
        retrieved_third = self.driver.retrieve_by_name(self.store, name, 3)

        # Verify

        self.assertEqual(3, len(self.driver.list(self.store)))

        self.assertEqual(retrieved_first.uuid, first.uuid)
        self.assertEqual(1, retrieved_first.version)
        self.assertEqual("YAML1", retrieved_first.contents)

        self.assertEqual(retrieved_second.uuid, second.uuid)
        self.assertEqual(2, retrieved_second.version)
        self.assertEqual("YAML2", retrieved_second.contents)

        self.assertEqual(retrieved_third.uuid, third.uuid)
        self.assertEqual(3, retrieved_third.version)
        self.assertEqual("YAML3", retrieved_third.contents)

    def test_retrieve_by_name_invalid_name(self):

        retrieve_by_name_call = partial(
            self.driver.retrieve_by_name,
            self.store, "name"
        )
        self.assertRaises(UnknownName, retrieve_by_name_call)

    def test_retrieve_by_name_invalid_version(self):

        self.driver.create(self.store, "name", "YAML")

        retrieve_by_name_call = partial(
            self.driver.retrieve_by_name,
            self.store, "name", 2
        )

        self.assertRaises(UnknownVersion, retrieve_by_name_call)
