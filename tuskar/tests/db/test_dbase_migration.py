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
from tuskar.tests.db import utils


#Since we only have one version right now can't really test 'migration'
#so just testing table definitions. This test file can be expanded later
class TestDbaseMigration(db_base.DbTestCase):

    def setUp(self):
        super(TestDbaseMigration, self).setUp()

    def tearDown(self):
        super(TestDbaseMigration, self).tearDown()

    def test_migration_ok(self):
        db_migration.db_sync()

    def test_v1_capacities_table_defined_ok(self):
        capacities = utils.get_db_table("capacities")
        capacities_col = {'id': 'Integer', 'name': 'String', 'value': 'String',
                          'unit': 'String', 'created_at': 'DateTime',
                          'updated_at': 'DateTime'}
        self._check_columns(capacities, capacities_col)

    def test_v1_racks_table_defined_ok(self):
        racks = utils.get_db_table("racks")
        racks_col = {'id': 'Integer', 'name': 'String', 'slots': 'Integer',
                     'state': 'String', 'subnet': 'String',
                     'location': 'String', 'resource_class_id': 'Integer',
                     'chassis_id': 'String', 'created_at': 'DateTime',
                     'updated_at': 'DateTime'}
        self._check_columns(racks, racks_col)

    def test_v1_nodes_table_defined_ok(self):
        nodes = utils.get_db_table("nodes")
        nodes_col = {'id': 'Integer', 'node_id': 'String',
                     'rack_id': 'Integer', 'created_at': 'DateTime',
                     'updated_at': 'DateTime'}
        self._check_columns(nodes, nodes_col)

    def test_v1_rack_capacities_table_defined_ok(self):
        rack_capacities = utils.get_db_table("rack_capacities")
        rack_capacities_col = {'id': 'Integer', 'capacity_id': 'Integer',
                               'rack_id': 'Integer', 'created_at': 'DateTime',
                               'updated_at': 'DateTime'}
        self._check_columns(rack_capacities, rack_capacities_col)

    def test_v1_flavor_capacities_table_defined_ok(self):
        flav_capacities = utils.get_db_table("flavor_capacities")
        flav_capacities_col = {'id': 'Integer', 'capacity_id': 'Integer',
                               'flavor_id': 'Integer',
                               'created_at': 'DateTime',
                               'updated_at': 'DateTime'}
        self._check_columns(flav_capacities, flav_capacities_col)

    def test_v1_resource_classes_table_defined_ok(self):
        resource_classes = utils.get_db_table("resource_classes")
        resource_classes_col = {'id': 'Integer', 'name': 'String',
                                'service_type': 'String',
                                'created_at': 'DateTime',
                                'updated_at': 'DateTime'}
        self._check_columns(resource_classes, resource_classes_col)

    def test_v1_flavors_table_defined_ok(self):
        flavors = utils.get_db_table("flavors")
        flavors_col = {'id': 'Integer', 'name': 'String',
                       'resource_class_id': 'Integer',
                       'nova_flavor_uuid': 'String', 'max_vms': 'Integer',
                       'created_at': 'DateTime', 'updated_at': 'DateTime'}
        self._check_columns(flavors, flavors_col)

    def test_non_existant_table_retrieve_fails(self):
        self.assertRaises(sqlalchemy.exc.NoSuchTableError,
                          utils.get_db_table, 'herpy')

    def _check_columns(self, table, column_types):
        for col, coltype in column_types.items():
            self.assertTrue(isinstance(table.columns[col].type,
                            getattr(sqlalchemy.types, coltype)))
