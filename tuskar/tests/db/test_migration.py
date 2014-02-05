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
from tuskar.openstack.common.db.sqlalchemy import session as db_session
from tuskar.tests.db import base as db_base


class CurrentDatabaseSchemaTests(db_base.DbTestCase):
    """Current schema verification.

    Contains tests that verify the end result of the migration matches
    the most recent schema.
    """

    def test_migration_ok(self):
        db_migration.db_sync()
        # Should not raise any exceptions

    def test_verify_overcloud_roles(self):
        table = self._get_db_table('overcloud_roles')
        expected = {
            'id': 'Integer',
            'name': 'String',
            'description': 'String',
            'image_name': 'String',
            'flavor_id': 'String',
            'created_at': 'DateTime',
            'updated_at': 'DateTime',
        }
        self._assert_columns(table, expected)

    def test_verify_overcloud(self):
        table = self._get_db_table('overclouds')
        expected = {
            'id': 'Integer',
            'name': 'String',
            'description': 'String',
            'created_at': 'DateTime',
            'updated_at': 'DateTime',
        }
        self._assert_columns(table, expected)

    def test_verify_overcloud_attributes(self):
        table = self._get_db_table('overcloud_attributes')
        expected = {
            'id': 'Integer',
            'overcloud_id': 'Integer',
            'key': 'String',
            'value': 'Text',
            'created_at': 'DateTime',
            'updated_at': 'DateTime',
        }
        self._assert_columns(table, expected)

    @staticmethod
    def _get_db_table(table_name):
        metadata = sqlalchemy.MetaData()
        metadata.bind = db_session.get_engine()
        return sqlalchemy.Table(table_name, metadata, autoload=True)

    def _assert_columns(self, table, column_types):
        for col, coltype in column_types.items():
            self.assertTrue(isinstance(table.columns[col].type,
                            getattr(sqlalchemy.types, coltype)))
