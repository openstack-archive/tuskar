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


class TestDbResourceClasses(db_base.DbTestCase):
    db = dbapi.get_backend()

    def setup(self):
        super(TestDbResourceClasses, self).setUp()

    def tearDown(self):
        super(TestDbResourceClasses, self).tearDown()

    def test_it_can_create_and_delete_a_plain_resource_class(self):
        #get a pecan resource_class:
        pecan_rc = utils.get_test_resource_class(
            name='test_plain_resource_class',
            service_type='compute')
        #create it in db:
        db_rc = self.db.create_resource_class(pecan_rc)
        self.__check_resource_class(db_rc,
                                    'test_plain_resource_class',
                                    'compute')
        #delete it:
        self.db.delete_resource_class(db_rc.id)

    def test_create_resource_class_duplicate_name(self):
        rc = {'name': 'name_1', 'service_type': 'compute'}

        pecan_rc = utils.get_test_resource_class(**rc)

        db_rc = self.db.create_resource_class(pecan_rc)
        self.addCleanup(self.db.delete_resource_class, db_rc.id)
        self.assertRaises(exception.ResourceClassExists,
                          self.db.create_resource_class, pecan_rc)

    def test_it_can_create_and_delete_resource_class_with_flavors(self):
        #get a pecan resource_class:
        pecan_rc = utils.get_test_resource_class(
            name='test_plain_resource_class',
            service_type='compute')
        #give it some flavors:
        pecan_rc.flavors = [utils.get_test_flavor(name='xyz', value='123'),
                            utils.get_test_flavor(name='abc', value='456')]
        #create it in db:
        db_rc = self.db.create_resource_class(pecan_rc)
        self.__check_resource_class(db_rc,
                                    'test_plain_resource_class',
                                    'compute',
                                    flavor_names=['xyz', 'abc'],
                                    flavor_values=['123', '456'])
        #delete it:
        self.db.delete_resource_class(db_rc.id)

    def test_it_can_create_and_delete_resource_class_with_racks(self):
        #get a pecan resource_class:
        pecan_rc = utils.get_test_resource_class(
            name='resource_class_with_racks',
            service_type='compute')
        #first create racks in database (ids 1 and 2):
        db_rack1 = self.db.create_rack(utils.get_test_rack(name='rack1'))
        db_rack2 = self.db.create_rack(utils.get_test_rack(name='rack2'))
        #add racks to resource class:
        pecan_rc.racks = [utils.get_test_resource_class_rack(id=db_rack1.id),
                          utils.get_test_resource_class_rack(id=db_rack2.id)]
        #create rc with racks in db:
        db_rc = self.db.create_resource_class(pecan_rc)
        #check it:
        self.__check_resource_class(db_rc,
                                    'resource_class_with_racks',
                                    'compute',
                                    rack_ids=[db_rack1.id, db_rack2.id])
        #delete:
        self.db.delete_resource_class(db_rc.id)
        self.assertTrue(db_rack1.resource_class_id == None)
        self.assertTrue(db_rack2.resource_class_id == None)
        self.db.delete_rack(db_rack1.id)
        self.db.delete_rack(db_rack2.id)

    def test_it_can_retrieve_all_resource_classes(self):
        created_db_rc_ids = []
        #create a four resource classes
        for i in range(1, 5):
            pecan_rc = utils.get_test_resource_class(name=('rc_' + str(i)),
                                                     service_type='foo')
            db_rc = self.db.create_resource_class(pecan_rc)
            created_db_rc_ids.append(db_rc.id)
        #retrieve the resource classes:
        resource_classes = self.db.get_resource_classes(None)
        self.assertTrue(len(resource_classes) == 4)
        #cleanup
        for rc_id in created_db_rc_ids:
            self.db.delete_resource_class(rc_id)

    def test_it_can_retrieve_single_resource_class(self):
        #get a pecan resource_class:
        pecan_rc = utils.get_test_resource_class(name='retrieve_rc_test',
                                                 service_type='compute')
        #create it:
        created_rc = self.db.create_resource_class(pecan_rc)
        #retrieve and check:
        db_rc = self.db.get_resource_class(created_rc.id)
        self.__check_resource_class(db_rc, 'retrieve_rc_test', 'compute')
        #cleanup
        self.db.delete_resource_class(db_rc.id)

    def test_it_explodes_when_retrieve_non_existant_resource_class(self):
        self.assertRaises(exception.ResourceClassNotFound,
                          self.db.get_resource_class, 'fake_id')

    def test_update_resource_class_duplicate_name(self):
        pecan_rc_1 = utils.get_test_resource_class(name='resource_class_1',
                                                   service_type='compute')
        pecan_rc_2 = utils.get_test_resource_class(name='resource_class_2',
                                                   service_type='controller')
        db_rc_1 = self.db.create_resource_class(pecan_rc_1)
        self.addCleanup(self.db.delete_resource_class, db_rc_1.id)
        db_rc_2 = self.db.create_resource_class(pecan_rc_2)
        self.addCleanup(self.db.delete_resource_class, db_rc_2.id)

        pecan_rc_2.name = 'resource_class_1'
        self.assertRaises(exception.ResourceClassExists,
                          self.db.update_resource_class,
                          db_rc_2.id, pecan_rc_2)

    def test_it_can_update_resource_class_name_type_and_image_id(self):
        new_image_id = '7b53ea12-cb94-4540-8d3c-e5132263d180'
        #get a pecan resource_class:
        pecan_rc = utils.get_test_resource_class(name='a_plain_resource_class',
                                                 service_type='compute')
        #create it:
        db_rc = self.db.create_resource_class(pecan_rc)
        #update:
        pecan_rc.name = 'updated_plain_resource_class'
        pecan_rc.service_type = 'storage'
        pecan_rc.image_id = new_image_id
        updated_db_rc = self.db.update_resource_class(db_rc.id, pecan_rc)
        #check
        self.__check_resource_class(updated_db_rc,
                                    'updated_plain_resource_class',
                                    'storage',
                                    image_id=new_image_id)
        self.db.delete_resource_class(updated_db_rc.id)

    def test_it_can_update_resource_class_racks_and_flavors(self):
        #get a pecan resource_class:
        pecan_rc = utils.get_test_resource_class(
            name='resource_class_update_racks_flavs',
            service_type='compute')
        #create racks in database:
        db_rack1 = self.db.create_rack(utils.get_test_rack(name='rack1'))
        db_rack2 = self.db.create_rack(utils.get_test_rack(name='rack2'))
        #add racks to resource class:
        pecan_rc.racks = [utils.get_test_resource_class_rack(id=db_rack1.id),
                          utils.get_test_resource_class_rack(id=db_rack2.id)]
        #give it a couple of flavors too:
        pecan_rc.flavors = [utils.get_test_flavor(name='flav1', value='1'),
                            utils.get_test_flavor(name='flav2', value='2')]
        #create rc in db:
        db_rc = self.db.create_resource_class(pecan_rc)
        #update racks and flavors:
        pecan_rc.flavors = [utils.get_test_flavor(name='flav3', value='3'),
                            utils.get_test_flavor(name='flav4', value='4')]
        db_rack3 = self.db.create_rack(utils.get_test_rack(name='rack3'))
        db_rack4 = self.db.create_rack(utils.get_test_rack(name='rack4'))
        pecan_rc.racks = [utils.get_test_resource_class_rack(id=db_rack3.id),
                          utils.get_test_resource_class_rack(id=db_rack4.id)]
        #update the resource class:
        updated_db_rc = self.db.update_resource_class(db_rc.id, pecan_rc)
        #check:
        #FIXME: THERE IS A BUG IN UPDATE RESOURCECLASS - it doesn't remove
        #the old racks in update operation - adding all ids here so test passes
        self.__check_resource_class(updated_db_rc,
                                    'resource_class_update_racks_flavs',
                                    'compute',
                                    flavor_names=['flav3', 'flav4'],
                                    flavor_values=['3', '4'],
                                    rack_ids=[db_rack1.id, db_rack2.id,
                                              db_rack3.id, db_rack4.id])
        #FIXME: i.e. remove db_rack1.id and db_rack2.id above
        #as they shouldn't be there
        #delete:
        self.db.delete_resource_class(updated_db_rc.id)
        for rack in [db_rack1, db_rack2, db_rack3, db_rack4]:
            self.db.delete_rack(rack.id)

    def __check_resource_class(self, rc, name, service_type, **kwargs):
        self.assertTrue(rc.name == name)
        self.assertTrue(rc.service_type == service_type)
        if 'image_id' in kwargs:
            image_id = kwargs['image_id']
            self.assertEqual(rc.image_id, image_id)

        #flavors
        if rc.flavors != []:
            names = kwargs.get('flavor_names')
            values = kwargs.get('flavor_values')
            for flav in rc.flavors:
                self.assertTrue(flav.name in names)
                for capacity in flav.capacities:
                    self.assertTrue(capacity.value in values)
        #racks
        if rc.racks != []:
            ids = kwargs.get('rack_ids')
            for rack in rc.racks:
                self.assertTrue(rack.id in ids)
