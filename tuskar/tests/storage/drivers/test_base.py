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

from sys import stdout

from mock import Mock

from tuskar.storage.drivers.base import BaseDriver
from tuskar.storage.stores import TemplateStore
from tuskar.tests.base import TestCase


class _DummyDriver(BaseDriver):

    def __init__(self, client, out=stdout):
        self.client = client
        self.out = out

    def _log(self, msg):
        self.out.write(msg)

    def create(self, store, name, contents):
        self._log("Creating {0} named {1}".format(store, name))
        return self.client.create(store, name, contents)

    def retrieve(self, store, uuid):
        self._log("Retrieving {0} with ID {1}".format(store, uuid))
        return self.client.retrieve(store, uuid)

    def update(self, store, uuid, name, contents):
        self._log("Updating {0} with ID {1}".format(store, uuid))
        return self.client.update(store, uuid, name, contents)

    def delete(self, store, uuid):
        self._log("Deleting {0} with ID {1}".format(store, uuid))
        self.client.delete(store, uuid)

    def list(self, store, only_latest=False):
        self._log("Listing {0}".format(store))
        self.client.list(store, only_latest=only_latest)

    def retrieve_by_name(self, store, name, version=None):
        self._log("Deleting {0} with name {1}".format(store, name))
        self.client.retrieve_by_name(store, name, version=version)


class BaseDriverTests(TestCase):

    def setUp(self):
        super(BaseDriverTests, self).setUp()

        self.mock_client = Mock()
        self.mock_stdout = Mock()
        self.driver = _DummyDriver(self.mock_client, out=self.mock_stdout)
        self.store = TemplateStore(self.driver)

    def test_create(self):
        self.driver.create(self.store, "swift.yaml", "YAML")
        self.mock_client.create.assert_called_once_with(
            self.store, "swift.yaml", "YAML")
        self.mock_client.create.assert_called_once_with(
            self.store, "swift.yaml", "YAML")

    def test_retrieve(self):

        self.driver.retrieve(self.store, "uuid")
        self.mock_client.retrieve.assert_called_once_with(self.store, "uuid")

    def test_update(self):
        self.driver.update(self.store, "uuid", "swift2.yaml", "YAML2")
        self.mock_client.update.assert_called_once_with(
            self.store, "uuid", "swift2.yaml", "YAML2")

    def test_delete(self):
        self.driver.delete(self.store, "uuid")
        self.mock_client.delete.assert_called_once_with(self.store, "uuid")

    def test_list(self):
        self.driver.list(self.store)
        self.mock_client.list.assert_called_once_with(
            self.store, only_latest=False)

        self.mock_client.list.reset_mock()

        self.store.list(only_latest=True)
        self.mock_client.list.assert_called_once_with(
            self.store, only_latest=True)

    def test_retrieve_by_name(self):

        self.driver.retrieve_by_name(self.store, "name")
        self.mock_client.retrieve_by_name.assert_called_once_with(
            self.store, "name", version=None)

        self.mock_client.retrieve_by_name.reset_mock()

        self.driver.retrieve_by_name(self.store, "name", version=2)
        self.mock_client.retrieve_by_name.assert_called_once_with(
            self.store, "name", version=2)
