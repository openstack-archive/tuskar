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

from unittest import TestCase

from mock import Mock

from tuskar.storage.drivers.dummy import DummyDriver
from tuskar.storage.stores import TemplateStore


class DummyDriverTests(TestCase):

    def setUp(self):

        self.mock_client = Mock()
        self.mock_stdout = Mock()
        self.driver = DummyDriver(self.mock_client)
        self.store = TemplateStore(self.driver)

    def test_create(self):
        self.driver.create(self, "swift.yaml", "YAML")
        self.mock_client.create.assert_called_once_with(
            self, "swift.yaml", "YAML")
        self.mock_client.create.assert_called_once_with(
            self, "swift.yaml", "YAML")

    def test_retrieve(self):

        self.driver.retrieve(self, "uuid")
        self.mock_client.retrieve.assert_called_once_with(self, "uuid")

    def test_update(self):
        self.driver.update(self, "uuid", "swift2.yaml", "YAML2")
        self.mock_client.update.assert_called_once_with(
            self, "uuid", "swift2.yaml", "YAML2")

    def test_delete(self):
        self.driver.delete(self, "uuid")
        self.mock_client.delete.assert_called_once_with(self, "uuid")

    def test_list(self):
        self.driver.list(self)
        self.mock_client.list.assert_called_once_with(self)
