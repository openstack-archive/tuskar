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

from tuskar.common import context as tuskar_context
from tuskar.storage.drivers.sqlalchemy import SQLAlchemyDriver
from tuskar.storage.stores import TemplateStore
from tuskar.tests import base


class SQLAlchemyDriverTestCase(base.TestCase):

    def setUp(self):
        super(SQLAlchemyDriverTestCase, self).setUp()

        self.context = tuskar_context.get_admin_context()
        self.driver = SQLAlchemyDriver()
        self.store = TemplateStore(self.driver)

    def test_create(self):
        result = self.driver.create(self.store, "swift.yaml", "YAML")

        self.assertEqual(result.uuid, '')

    def test_retrieve(self):

        self.driver.retrieve(self.store, "uuid")

    def test_update(self):
        self.driver.update(self.store, "uuid", "swift2.yaml", "YAML2")

    def test_delete(self):
        self.driver.delete(self.store, "uuid")

    def test_list(self):
        self.driver.list(self.store)

    def test_retrieve_by_name(self):

        self.driver.create(self.store, "name", "YAML")

        self.driver.retrieve_by_name(self.store, "name")
