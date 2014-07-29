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

from datetime import datetime

from mock import Mock

from tuskar.storage.models import StoredFile
from tuskar.storage.stores import TemplateStore
from tuskar.tests.base import TestCase


class ModelsTests(TestCase):

    def setUp(self):
        super(ModelsTests, self).setUp()

        self.driver = Mock()
        self.store = TemplateStore(self.driver)

    def test_str(self):

        uuid = "d131dd02c5e6eec4"
        f = StoredFile(uuid, "stored contents", self.store)

        self.assertEqual(str(f), "template with ID d131dd02c5e6eec4")

    def test_str_datetimes(self):

        dt = datetime.now()

        uuid = "d131dd02c5e6eec5"
        f = StoredFile(uuid, "stored contents", self.store, created_at=dt,
                       updated_at=dt)

        self.assertEqual(str(f), "template with ID d131dd02c5e6eec5")

    def test_str_version(self):

        uuid = "d131dd02c5e6eec6"
        f = StoredFile(uuid, "stored contents", self.store, version=1)

        self.assertEqual(str(f), "template with ID d131dd02c5e6eec6")

    def test_str_name(self):

        uuid = "d131dd02c5e6eec7"
        f = StoredFile(uuid, "stored contents", self.store, name="test")

        self.assertEqual(
            str(f), "template with ID d131dd02c5e6eec7 and name test")
