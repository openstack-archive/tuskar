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

from abc import ABCMeta
from abc import abstractmethod
from datetime import datetime
from functools import partial

from six import add_metaclass

from tuskar.storage import exceptions
from tuskar.storage import stores
from tuskar.tests.base import TestCase


@add_metaclass(ABCMeta)
class BaseDriverTestCase(TestCase):

    @abstractmethod
    def _get_driver(self):
        pass

    def setUp(self):

        super(BaseDriverTestCase, self).setUp()

        self.driver = self._get_driver()
        self.store = self._get_store(self.driver)


@add_metaclass(ABCMeta)
class BaseTestsMixin(object):

    @abstractmethod
    def _get_store(self, driver):
        pass


class BaseStoreMixin(BaseTestsMixin):

    def _get_store(self, driver):

        class BaseStore(stores._BaseStore):
            object_type = "base_object"

        return BaseStore(driver)

    def _create_test_object(self, i=None):
        return self.store.create("YAML")

    def test_create(self):

        # Test
        result = self.store.create("YAML")

        # Verify
        self.assertNotEqual(result.uuid, None)
        self.assertEqual(result.contents, "YAML")
        self.assertEqual(result.name, None)
        self.assertEqual(type(result.created_at), datetime)
        self.assertEqual(result.updated_at, None)

    def test_version(self):
        # Test
        result = self._create_test_object()

        # Verify
        self.assertEqual(result.version, None)

    def test_retrieve(self):

        # Setup
        created = self._create_test_object()

        # Test
        result = self.store.retrieve(created.uuid)

        # Verify
        self.assertEqual(result.uuid, created.uuid)
        self.assertEqual(result.contents, created.contents)
        self.assertEqual(result.name, created.name)
        self.assertEqual(result.created_at, created.created_at)
        self.assertEqual(result.updated_at, created.updated_at)
        self.assertEqual(result.version, created.version)
        self.assertEqual(result, created)

    def test_update(self):

        # Setup
        created = self._create_test_object()

        # Test
        result = self.store.update(created.uuid, "YAML 2")

        # Verify
        self.assertEqual(result.uuid, created.uuid)
        self.assertEqual(result.contents, "YAML 2")
        self.assertEqual(result.name, created.name)
        self.assertEqual(result.created_at, created.created_at)
        self.assertEqual(type(result.updated_at), datetime)
        self.assertEqual(result.version, created.version)

    def test_delete(self):

        # Setup
        created = self._create_test_object()

        # Test
        result = self.store.delete(created.uuid)

        # Verify
        self.assertEqual(None, result)
        retrieve_call = partial(self.store.retrieve, created.uuid)
        self.assertRaises(exceptions.UnknownUUID, retrieve_call)

    def test_list(self):

        # Setup
        created_files = [self._create_test_object(i) for i in range(5)]

        # Test
        listed_files = self.store.list()

        # Verify
        self.assertEqual(5, len(listed_files))
        self.assertEqual(created_files, listed_files)


class NamedStoreMixin(BaseStoreMixin):

    def _get_store(self, driver):

        class NamedStore(stores._NamedStore):
            object_type = "named_object"

        return NamedStore(driver)

    def _create_test_object(self, i=None):
        suffix = '' if i is None else " {0}".format(i)
        return self.store.create("NAME{0}".format(suffix), "YAML")

    def test_create(self):

        # Test
        result = self.store.create("NAME", "YAML")

        # Verify
        self.assertNotEqual(result.uuid, None)
        self.assertEqual(result.contents, "YAML")
        self.assertEqual(result.name, "NAME")
        self.assertEqual(type(result.created_at), datetime)
        self.assertEqual(result.updated_at, None)

    def test_retrieve(self):

        # Setup
        created = self._create_test_object()

        # Test
        result = self.store.retrieve(created.uuid)

        # Verify
        self.assertEqual(result.uuid, created.uuid)
        self.assertEqual(result.contents, created.contents)
        self.assertEqual(result.name, created.name)
        self.assertEqual(result.created_at, created.created_at)
        self.assertEqual(result.updated_at, created.updated_at)
        self.assertEqual(result.version, created.version)
        self.assertEqual(result, created)

    def test_retrieve_by_name(self):

        # Setup
        created = self._create_test_object()

        # Test
        result = self.store.retrieve_by_name(created.name)

        # Verify
        self.assertEqual(result.uuid, created.uuid)
        self.assertEqual(result.contents, created.contents)
        self.assertEqual(result.name, created.name)
        self.assertEqual(result.created_at, created.created_at)
        self.assertEqual(result.updated_at, created.updated_at)
        self.assertEqual(result.version, created.version)
        self.assertEqual(result, created)


class VersionedStoreMixin(NamedStoreMixin):

    def _get_store(self, driver):

        class VersionedStore(stores._VersionedStore):
            object_type = "versioned_object"

        return VersionedStore(driver)

    def test_version(self):
        # Test
        result = self._create_test_object()

        # Verify
        self.assertEqual(result.version, 1)

    def test_update(self):

        # Setup
        created = self._create_test_object()

        # Test
        result = self.store.update(created.uuid, "YAML 2")

        # Verify
        self.assertNotEqual(result.uuid, created.uuid)
        self.assertEqual(result.contents, "YAML 2")
        self.assertEqual(result.name, created.name)
        self.assertNotEqual(result.created_at, created.created_at)
        self.assertEqual(result.updated_at, None)
        self.assertEqual(created.version, 1)
        self.assertEqual(result.version, 2)

    def test_retrieve_by_name_and_version(self):

        # Setup
        created = self._create_test_object()

        # Test
        result = self.store.retrieve_by_name(
            created.name, version=created.version)

        # Verify
        self.assertEqual(result.uuid, created.uuid)
        self.assertEqual(result.contents, created.contents)
        self.assertEqual(result.name, created.name)
        self.assertEqual(result.created_at, created.created_at)
        self.assertEqual(result.updated_at, created.updated_at)
        self.assertEqual(result.version, created.version)
        self.assertEqual(result, created)

    def test_retrieve_by_name_and_version_fail(self):

        # Setup
        created = self._create_test_object()

        # Verify
        retrieve_call = partial(self.store.retrieve_by_name,
                                created.name, 2)
        self.assertRaises(exceptions.UnknownVersion, retrieve_call)

    def test_list_only_latest(self):

        # Setup
        created_files = [self._create_test_object(i) for i in range(5)]

        updated = [self.store.update(created.uuid, "YAML 2")
                   for created in created_files]

        # Test
        listed_files = self.store.list(only_latest=True)

        # Verify
        self.assertEqual(5, len(listed_files))
        self.assertEqual(5, len(updated))
        self.assertEqual(updated, listed_files)
