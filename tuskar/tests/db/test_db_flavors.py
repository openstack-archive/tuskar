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


class TestDbFlavors(db_base.DbTestCase):
    db = dbapi.get_backend()

    def setup(self):
        super(TestDbFlavors, self).setUp()

    def tearDown(self):
        super(TestDbFlavors, self).tearDown()

    #exercises 'def create_resource_class' for flavors
    def test_it_can_create_flavors_during_resource_class_create(self):
        #get a pecan resource_class:
        rc = utils.get_test_resource_class()
        #add some flavors:
        rc.flavors = [utils.get_test_flavor(name='a', value='9'),
                      utils.get_test_flavor(name='b', value='8'),
                      utils.get_test_flavor(name='c', value='7')]
        #create rc with flavors in database
        db_rc = self.db.create_resource_class(rc)
        #check the flavors are ok:
        self.__check_flavor_capacities(db_rc.flavors, ['a', 'b', 'c'],
                                                      ['7', '8', '9'])
        #cleanup
        self.db.delete_resource_class(db_rc.id)

    def test_it_can_update_resource_class_flavors(self):
        #create a resource class
        pecan_rc = utils.get_test_resource_class()
        #give it a flavor:
        pecan_rc.flavors = [utils.get_test_flavor(name='foo', value='99')]
        db_rc = self.db.create_resource_class(pecan_rc)
        #update the resource class with new flavors:
        pecan_rc.flavors = [utils.get_test_flavor(name='one', value='1'),
                            utils.get_test_flavor(name='two', value='2'),
                            utils.get_test_flavor(name='three', value='3')]
        #call the update
        updated_rc = self.db.update_resource_class(db_rc.id, pecan_rc)
        #make test assertions
        self.__check_flavor_capacities(updated_rc.flavors,
                                       ['one', 'two', 'three'],
                                       ['1', '2', '3'])
        #cleanup
        self.db.delete_resource_class(db_rc.id)

    def test_it_can_create_a_resource_class_flavor(self):
        #create a resource class:
        pecan_rc = utils.get_test_resource_class()
        db_rc = self.db.create_resource_class(pecan_rc)
        #get a pecan flavor to add:
        pecan_flavor = utils.get_test_flavor(name='bar', value='333')
        db_flavor = self.db.create_resource_class_flavor(db_rc.id,
                                                         pecan_flavor)
        #make test assertions
        self.__check_flavor_capacities([db_flavor], ['bar'], ['333'])
        #cleanup
        self.db.delete_resource_class(db_rc.id)

    def test_it_can_update_a_resource_class_flavor(self):
        #create a resource class
        pecan_rc = utils.get_test_resource_class()
        #give it a couple flavors and create it
        pecan_rc.flavors = [utils.get_test_flavor(name='xyz', value='123'),
                            utils.get_test_flavor(name='abc', value='456')]
        db_rc = self.db.create_resource_class(pecan_rc)
        # we cannot rely on the order of the db_rc.flavors items
        if db_rc.flavors[0].name == 'xyz':
            xyz_flavor = db_rc.flavors[0]
        else:
            xyz_flavor = db_rc.flavors[1]
        #now update one of the flavors:
        updated_flav = self.db.update_resource_class_flavor(
            db_rc.id,
            xyz_flavor.id,
            utils.get_test_flavor(name='xyz', value='999'))
        #retrieve updated rc and assert:
        updated_rc = self.db.get_resource_class(db_rc.id)
        self.__check_flavor_capacities(updated_rc.flavors,
                                       ['xyz', 'abc'],
                                       ['999', '456'])
        #cleanup
        self.db.delete_resource_class(db_rc.id)

    def test_it_can_retrieve_all_flavors_for_resource_class(self):
        #create a resource class
        pecan_rc = utils.get_test_resource_class()
        #give it a couple flavors and create it
        pecan_rc.flavors = [utils.get_test_flavor(name='xyz', value='123'),
                            utils.get_test_flavor(name='abc', value='456')]
        db_rc = self.db.create_resource_class(pecan_rc)
        #retrieve the flavors:
        flavs = self.db.get_flavors(db_rc.id)
        self.__check_flavor_capacities(flavs, ['xyz', 'abc'], ['123', '456'])
        #cleanup
        self.db.delete_resource_class(db_rc.id)

    def test_it_can_retrieve_a_single_flavor(self):
        #create a resource class
        pecan_rc = utils.get_test_resource_class()
        #give it a couple flavors and create it
        pecan_rc.flavors = [utils.get_test_flavor(name='xyz', value='123'),
                            utils.get_test_flavor(name='abc', value='456')]
        db_rc = self.db.create_resource_class(pecan_rc)
        # we cannot rely on the order of the db_rc.flavors items
        if db_rc.flavors[0].name == 'abc':
            abc_flavor = db_rc.flavors[0]
        else:
            abc_flavor = db_rc.flavors[1]
        #retrieve a specific flavor
        flav = self.db.get_flavor(abc_flavor.id)
        self.__check_flavor_capacities([flav], ['abc'], ['456'])
        #cleanup
        self.db.delete_resource_class(db_rc.id)

    def test_it_explodes_if_get_non_existant_flavor(self):
        self.assertRaises(exception.FlavorNotFound,
                          self.db.get_flavor,
                          'fake_id')

    def __check_flavor_capacities(self, flavors, names, values):
        for flav in flavors:
            self.assertTrue(flav.name in names)
            for capacity in flav.capacities:
                self.assertTrue(capacity.value in values)
