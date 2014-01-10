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

from tuskar.db.sqlalchemy import api as dbapi
from tuskar.db.sqlalchemy import models
from tuskar.tests.db import base as db_base


class ResourceCategoryTests(db_base.DbTestCase):

    def setUp(self):
        super(ResourceCategoryTests, self).setUp()

        self.connection = dbapi.Connection()

    def test_create(self):
        # Setup
        save_me = models.ResourceCategory()
        save_me.name = 'cat-1'
        save_me.description = 'desc-1'
        save_me.image_id = 'abcdef'

        # Test
        self.connection.create_resource_category(save_me)

        # Verify
        found = self.connection.get_resource_categories()

        self.assertEqual(1, len(found))
