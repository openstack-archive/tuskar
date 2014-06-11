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

from tuskar.common import exception
from tuskar.db.sqlalchemy import api as dbapi
from tuskar.db.sqlalchemy import models
from tuskar.tests.db import base as db_base


class OvercloudRoleTests(db_base.DbTestCase):

    def setUp(self):
        super(OvercloudRoleTests, self).setUp()

        self.connection = dbapi.Connection()

        self.save_me_1 = models.OvercloudRole(
            name='name-1',
            description='desc-1',
            image_name='image-1',
            flavor_id='tuvwxyz',
        )

        self.save_me_2 = models.OvercloudRole(
            name='name-2',
            description='desc-2',
            image_name='image-2',
            flavor_id='abc',
        )

    def test_create_overcloud_role(self):
        # Test
        saved = self.connection.create_overcloud_role(self.save_me_1)

        # Verify
        self.assertTrue(saved is not None)
        self.assertTrue(saved.id is not None)
        self.assertEqual(saved.name, self.save_me_1.name)
        self.assertEqual(saved.description, self.save_me_1.description)
        self.assertEqual(saved.image_name, self.save_me_1.image_name)
        self.assertEqual(saved.flavor_id, self.save_me_1.flavor_id)

        # Simple check to make sure it can be pulled out of the DB
        found = self.connection.get_overcloud_roles()
        self.assertEqual(1, len(found))
        self.assertEqual(found[0].id, saved.id)

    def test_create_overcloud_role_duplicate_name(self):
        # Setup
        self.connection.create_overcloud_role(self.save_me_1)
        duplicate = models.OvercloudRole(
            name=self.save_me_1.name,
            description='irrelevant',
            image_name='irrelevant'
        )

        # Test
        self.assertRaises(exception.OvercloudRoleExists,
                          self.connection.create_overcloud_role,
                          duplicate)

    def test_update(self):
        # Setup
        saved = self.connection.create_overcloud_role(self.save_me_1)

        # Test
        delta = models.OvercloudRole(
            id=saved.id,
            image_name='abcdef',
            flavor_id='new-flavor'
        )
        self.connection.update_overcloud_role(delta)

        # Verify
        found = self.connection.get_overcloud_role_by_id(saved.id)
        self.assertEqual(found.image_name, delta.image_name)
        self.assertEqual(found.flavor_id, delta.flavor_id)

    def test_delete(self):
        # Setup
        saved = self.connection.create_overcloud_role(self.save_me_1)

        # Test
        self.connection.delete_overcloud_role_by_id(saved.id)

        # Verify
        found = self.connection.get_overcloud_roles()
        self.assertEqual(0, len(found))

    def test_delete_nonexistent_role(self):
        self.assertRaises(exception.OvercloudRoleNotFound,
                          self.connection.delete_overcloud_role_by_id,
                          'fake-id')

    def test_get_overcloud_roles(self):
        # Setup
        self.connection.create_overcloud_role(self.save_me_1)
        self.connection.create_overcloud_role(self.save_me_2)

        # Test
        all_roles = self.connection.get_overcloud_roles()

        # Verify
        self.assertEqual(2, len(all_roles))

        found_1 = all_roles[0]
        self.assertEqual(found_1.name, self.save_me_1.name)
        self.assertEqual(found_1.description, self.save_me_1.description)
        self.assertEqual(found_1.image_name, self.save_me_1.image_name)

        found_2 = all_roles[1]
        self.assertEqual(found_2.name, self.save_me_2.name)
        self.assertEqual(found_2.description, self.save_me_2.description)
        self.assertEqual(found_2.image_name, self.save_me_2.image_name)

    def test_get_overcloud_roles_no_results(self):
        # Test
        all_roles = self.connection.get_overcloud_roles()

        # Verify
        self.assertTrue(isinstance(all_roles, list))
        self.assertEqual(0, len(all_roles))

    def test_get_overcloud_role_by_id(self):
        # Setup
        self.connection.create_overcloud_role(self.save_me_1)
        saved_2 = self.connection.create_overcloud_role(self.save_me_2)

        # Test
        found = self.connection.get_overcloud_role_by_id(saved_2.id)

        # Verify
        self.assertTrue(found is not None)
        self.assertEqual(found.id, saved_2.id)
        self.assertEqual(found.name, saved_2.name)

    def test_get_overcloud_role_by_id_no_result(self):
        self.assertRaises(exception.OvercloudRoleNotFound,
                          self.connection.get_overcloud_role_by_id,
                          'fake-id')


class OvercloudTests(db_base.DbTestCase):

    def setUp(self):
        super(OvercloudTests, self).setUp()

        self.connection = dbapi.Connection()

        self.role_1 = models.OvercloudRole(
            name='name-1',
            description='desc-1',
            image_name='image-1',
            flavor_id='tuvwxyz',
        )
        self.saved_role = self.connection.create_overcloud_role(self.role_1)

        self.attributes_1 = models.OvercloudAttribute(
            key='key-1',
            value='value-1',
        )

        self.attributes_2 = models.OvercloudAttribute(
            key='key-2',
            value='value-2',
        )

        self.count_1 = models.OvercloudRoleCount(
            overcloud_role_id=self.saved_role.id,
            num_nodes=4,
        )

        self.overcloud_1 = models.Overcloud(
            name='overcloud-1',
            description='desc-1',
            attributes=[self.attributes_1, self.attributes_2],
            counts=[self.count_1]
        )

        self.overcloud_2 = models.Overcloud(
            name='overcloud-2',
            description='desc-2',
            attributes=[]
        )

    def test_create_overcloud(self):
        # Test
        self.connection.create_overcloud_role(self.role_1)
        saved = self.connection.create_overcloud(self.overcloud_1)

        # Verify
        self.assertTrue(saved is not None)

        # IDs are populated
        self.assertTrue(saved.id is not None)
        for attribute in saved.attributes:
            self.assertTrue(attribute.id is not None)

        # Data integrity
        self.assertEqual(saved.name, self.overcloud_1.name)
        self.assertEqual(saved.description, self.overcloud_1.description)

        for index, attribute in enumerate(self.overcloud_1.attributes):
            self.assertEqual(saved.attributes[index].key, attribute.key)
            self.assertEqual(saved.attributes[index].value, attribute.value)

        for index, count in enumerate(self.overcloud_1.counts):
            self.assertEqual(saved.counts[index].overcloud_role_id,
                             count.overcloud_role_id)
            self.assertTrue(saved.counts[index] is not None)
            self.assertTrue(isinstance(saved.counts[index].overcloud_role,
                                       models.OvercloudRole))
            self.assertEqual(saved.counts[index].overcloud_role.name,
                             self.role_1.name)
            self.assertEqual(saved.counts[index].overcloud_role.description,
                             self.role_1.description)
            self.assertEqual(saved.counts[index].overcloud_role.image_name,
                             self.role_1.image_name)

            self.assertEqual(saved.counts[index].num_nodes,
                             count.num_nodes)

    def test_create_minimal_overcloud(self):
        # Setup
        overcloud = models.Overcloud(name='minimal')

        # Test
        saved = self.connection.create_overcloud(overcloud)

        # Verify
        self.assertEqual(saved.name, overcloud.name)
        self.assertEqual(saved.description, None)
        self.assertEqual(saved.attributes, [])
        self.assertEqual(saved.counts, [])

    def test_create_overcloud_duplicate_name(self):
        # Setup
        self.connection.create_overcloud(self.overcloud_1)
        duplicate = models.Overcloud(
            name=self.overcloud_1.name,
            description='irrelevant',
        )

        # Test
        self.assertRaises(exception.OvercloudExists,
                          self.connection.create_overcloud,
                          duplicate)

    def test_create_overcloud_duplicate_attribute(self):
        # Setup
        duplicate_attribute = models.OvercloudAttribute(
            key=self.attributes_1.key,
            value='irrelevant'
        )
        self.overcloud_1.attributes = [self.attributes_1, duplicate_attribute]

        # Test
        self.assertRaises(exception.DuplicateAttribute,
                          self.connection.create_overcloud,
                          self.overcloud_1)

    def test_update_overcloud(self):
        # Setup
        saved = self.connection.create_overcloud(self.overcloud_1)

        # Test
        saved.stack_id = 'new_id'
        self.connection.update_overcloud(saved)

        # Verify
        found = self.connection.get_overcloud_by_id(saved.id)
        self.assertEqual(found.stack_id, saved.stack_id)
        self.assertEqual(found.name, self.overcloud_1.name)

    def test_update_overcloud_attributes(self):
        # Setup

        # Add a third attribute for enough data
        self.overcloud_1.attributes.append(models.OvercloudAttribute(
            key='key-3',
            value='value-3',
        ))
        saved = self.connection.create_overcloud(self.overcloud_1)

        # Test
        # - Ignore the first
        saved.attributes.pop(0)

        # - Change the second
        saved.attributes[0].value = 'updated-2'

        # - Delete the third
        saved.attributes[1].value = None

        # - Add a fourth
        saved.attributes.append(models.OvercloudAttribute(
            key='key-4',
            value='value-4',
        ))

        self.connection.update_overcloud(saved)

        # Verify
        found = self.connection.get_overcloud_by_id(saved.id)

        self.assertEqual(3, len(found.attributes))
        self.assertEqual(found.attributes[0].key, 'key-1')
        self.assertEqual(found.attributes[0].value, 'value-1')
        self.assertEqual(found.attributes[1].key, 'key-2')
        self.assertEqual(found.attributes[1].value, 'updated-2')
        self.assertEqual(found.attributes[2].key, 'key-4')
        self.assertEqual(found.attributes[2].value, 'value-4')

    def test_update_overcloud_counts(self):

        # Setup

        # Roles
        role_2 = self.connection.create_overcloud_role(models.OvercloudRole(
            name='name-2',
        ))
        role_3 = self.connection.create_overcloud_role(models.OvercloudRole(
            name='name-3',
        ))
        role_4 = self.connection.create_overcloud_role(models.OvercloudRole(
            name='name-4',
        ))

        # Add extra counts for enough data
        self.overcloud_1.counts.append(models.OvercloudRoleCount(
            overcloud_role_id=role_2.id,
            num_nodes=2,
        ))
        self.overcloud_1.counts.append(models.OvercloudRoleCount(
            overcloud_role_id=role_3.id,
            num_nodes=3,
        ))
        saved = self.connection.create_overcloud(self.overcloud_1)

        # Test
        # - Ignore the first
        saved.counts.pop(0)

        # - Change the second
        saved.counts[0].num_nodes = 100

        # - Delete the third
        saved.counts[1].num_nodes = 0

        # - Add a fourth
        saved.counts.append(models.OvercloudRoleCount(
            overcloud_role_id=role_4.id,
            num_nodes=4,
        ))

        self.connection.update_overcloud(saved)

        # Verify
        found = self.connection.get_overcloud_by_id(saved.id)

        self.assertEqual(3, len(found.counts))
        self.assertEqual(found.counts[0].overcloud_role_id, self.saved_role.id)
        self.assertEqual(found.counts[0].num_nodes, 4)
        self.assertEqual(found.counts[1].overcloud_role_id, role_2.id)
        self.assertEqual(found.counts[1].num_nodes, 100)
        self.assertEqual(found.counts[2].overcloud_role_id, role_4.id)
        self.assertEqual(found.counts[2].num_nodes, 4)

    def test_update_nonexistent(self):
        fake = models.Overcloud(id='fake')
        self.assertRaises(exception.OvercloudNotFound,
                          self.connection.update_overcloud,
                          fake)

    def test_delete_overcloud(self):
        # Setup
        saved = self.connection.create_overcloud(self.overcloud_1)

        # Test
        self.connection.delete_overcloud_by_id(saved.id)

        # Verify
        found = self.connection.get_overclouds()
        self.assertEqual(0, len(found))

        # Ensure the joined tables are clear too
        session = dbapi.get_session()
        all_counts = session.query(models.OvercloudAttribute).all()
        session.close()
        self.assertEqual(0, len(all_counts))

        session = dbapi.get_session()
        all_counts = session.query(models.OvercloudRoleCount).all()
        session.close()
        self.assertEqual(0, len(all_counts))

    def test_delete_nonexistent_overcloud(self):
        self.assertRaises(exception.OvercloudNotFound,
                          self.connection.delete_overcloud_by_id,
                          'irrelevant-id')

    def test_get_overclouds(self):

        # This test also verifies that the attributes are eagerly loaded

        # Setup
        self.connection.create_overcloud(self.overcloud_1)
        self.connection.create_overcloud(self.overcloud_2)

        # Test
        all_overclouds = self.connection.get_overclouds()

        # Verify
        self.assertEqual(2, len(all_overclouds))

        found_1 = all_overclouds[0]
        self.assertEqual(found_1.name, self.overcloud_1.name)
        self.assertEqual(found_1.description, self.overcloud_1.description)
        self.assertEqual(found_1.attributes, self.overcloud_1.attributes)

        found_2 = all_overclouds[1]
        self.assertEqual(found_2.name, self.overcloud_2.name)
        self.assertEqual(found_2.description, self.overcloud_2.description)
        self.assertEqual(found_2.attributes, self.overcloud_2.attributes)

    def test_get_overclouds_no_results(self):
        # Test
        all_overclouds = self.connection.get_overclouds()

        # Verify
        self.assertTrue(isinstance(all_overclouds, list))
        self.assertEqual(0, len(all_overclouds))

    def test_get_overcloud_by_id(self):
        # Setup
        self.connection.create_overcloud(self.overcloud_1)
        saved_2 = self.connection.create_overcloud(self.overcloud_2)

        # Test
        found = self.connection.get_overcloud_by_id(saved_2.id)

        # Verify
        self.assertTrue(found is not None)
        self.assertEqual(found.id, saved_2.id)
        self.assertEqual(found.name, saved_2.name)

    def test_get_overcloud_by_id_no_result(self):
        self.assertRaises(exception.OvercloudNotFound,
                          self.connection.get_overcloud_by_id,
                          'fake-id')
