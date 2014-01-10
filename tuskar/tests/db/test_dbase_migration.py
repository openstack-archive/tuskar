# Copyright (c) 2013 Red Hat
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sqlalchemy
from tuskar.db import migration as db_migration
from tuskar.tests.db import base as db_base


#Since we only have one version right now can't really test 'migration'
#so just testing table definitions. This test file can be expanded later
class TestDbaseMigration(db_base.DbTestCase):

    def setUp(self):
        super(TestDbaseMigration, self).setUp()

    def tearDown(self):
        super(TestDbaseMigration, self).tearDown()

    def test_migration_ok(self):
        db_migration.db_sync()

    def _check_columns(self, table, column_types):
        for col, coltype in column_types.items():
            self.assertTrue(isinstance(table.columns[col].type,
                            getattr(sqlalchemy.types, coltype)))
