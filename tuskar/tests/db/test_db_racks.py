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

from tuskar.common import exception
from tuskar.db.sqlalchemy import api as dbapi
from tuskar.tests.db import base as db_base
from tuskar.tests.db import utils


class TestDbRacks(db_base.DbTestCase):
    db = dbapi.get_backend()

    def setUp(self):
        super(TestDbRacks, self).setUp()
        #need two resource classes - one for each rack:
        pecan_rc1 = utils.get_test_resource_class(name='rc1', type='compute')
        pecan_rc2 = utils.get_test_resource_class(name='rc2', type='control')
        #create the rc in the db
        self.db_rc1 = self.db.create_resource_class(pecan_rc1)
        self.db_rc2 = self.db.create_resource_class(pecan_rc2)
        #define 2 pecan racks, one without nodes:
        pecan_rack1 = utils.get_test_rack(name='rack_no_nodes',
                                          resource_class=True,
                                          rc_id=self.db_rc1.id)
        pecan_rack2 = utils.get_test_rack(name='rack_has_nodes',
                                          nodes=True,
                                          resource_class=True,
                                          rc_id=self.db_rc2.id)
        #create them in db
        self.rack1 = self.db.create_rack(pecan_rack1)
        self.rack2 = self.db.create_rack(pecan_rack2)

    def tearDown(self):
        super(TestDbRacks, self).tearDown()
        #cleanup
        self.db.delete_resource_class(self.db_rc1.id)
        self.db.delete_resource_class(self.db_rc2.id)
        self.db.delete_rack(self.rack1.id)
        self.db.delete_rack(self.rack2.id)

    def test_it_can_get_all_racks(self):
        db_racks = self.db.get_racks(None)
        self.__check_racks(db_racks, ['rack_no_nodes', 'rack_has_nodes'])
        self.assertTrue(len(db_racks) == 2)

    def test_it_can_get_specific_rack(self):
        rack = self.db.get_rack(self.rack1.id)
        self.__check_racks([rack], ['rack_no_nodes'])

    def test_it_explodes_when_get_non_existant_rack(self):
        self.assertRaises(exception.RackNotFound, self.db.get_rack, 'fack_id')

    def test_it_can_create_a_rack_without_nodes(self):
        #get rack without nodes:
        pecan_rack = utils.get_test_rack(name='rack_without_nodes')
        #create it:
        db_rack = self.db.create_rack(pecan_rack)
        self.__check_racks([db_rack], ['rack_without_nodes'])
        #cleanup
        self.db.delete_rack(db_rack.id)

    def test_it_can_create_a_rack_with_nodes(self):
        #define pecan rack with nodes
        pecan_rack = utils.get_test_rack(name='rack_with_nodes', nodes=True)
        #create:
        db_rack = self.db.create_rack(pecan_rack)
        self.__check_racks([db_rack], ['rack_with_nodes'])
        #cleanup
        self.db.delete_rack(db_rack.id)

    def test_it_can_update_rack_basic_attributes(self):
        #define a pecan rack:
        pecan_rack = utils.get_test_rack(name='a_rack',
                                         slots=1,
                                         subnet='192.168.0.0/16')
        #create in db:
        db_rack = self.db.create_rack(pecan_rack)
        #now update it
        pecan_rack.name = 'b_rack'
        pecan_rack.slots = 2
        pecan_rack.subnet = '10.0.0.0/24'
        db_rack = self.db.update_rack(db_rack.id, pecan_rack)
        self.__check_racks([db_rack], ['b_rack'])
        self.assertTrue(db_rack.slots == 2)
        self.assertTrue(db_rack.subnet == '10.0.0.0/24')
        #cleanup
        self.db.delete_rack(db_rack.id)

    def test_it_can_update_rack_nodes(self):
        #define a pecan rack with nodes:
        pecan_rack = utils.get_test_rack(name='rack_1', nodes=True)
        #create in db
        db_rack = self.db.create_rack(pecan_rack)
        #update nodes:
        pecan_rack.nodes = []
        for i in range(1, 11):
            pecan_rack.nodes.append(utils.get_test_rack_node(id=str(i)))
        db_rack = self.db.update_rack(db_rack.id, pecan_rack)
        self.__check_racks([db_rack], ['rack_1'])
        self.assertTrue(len(db_rack.nodes) == 10)
        for i in range(11, 16):
            pecan_rack.nodes.append(utils.get_test_rack_node(id=str(i)))
        db_rack = self.db.update_rack(db_rack.id, pecan_rack)
        self.assertEqual([n.node_id for n in db_rack.nodes],
                         [str(i) for i in range(1, 16)])
        #cleanup
        self.db.delete_rack(db_rack.id)

    def __check_racks(self, racks, names):
        for rack in racks:
            self.assertTrue(rack.name in names)
            self.assertTrue(rack.id != None)
            self.assertTrue(rack.slots != None)
            self.assertTrue(len(rack.capacities) > 0)
            self.assertTrue(rack.subnet != None)
            for capacity in rack.capacities:
                self.assertTrue(capacity.name in ['total_cpu', 'total_memory'])
