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

from tuskar.common import exception
from tuskar.db.sqlalchemy import api as dbapi
from tuskar.db.sqlalchemy import models
from tuskar.tests.db import base as db_base


class ResourceCategoryTests(db_base.DbTestCase):

    def setUp(self):
        super(ResourceCategoryTests, self).setUp()

        self.connection = dbapi.Connection()

        self.save_me_1 = models.ResourceCategory(
            name='name-1',
            description='desc-1',
            image_id='abcdef'
        )

        self.save_me_2 = models.ResourceCategory(
            name='name-2',
            description='desc-2',
            image_id='xyz'
        )

    def test_save_resource_category(self):
        # Test
        saved = self.connection.save_resource_category(self.save_me_1)

        # Verify
        self.assertTrue(saved is not None)
        self.assertTrue(saved.id is not None)
        self.assertEqual(saved.name, self.save_me_1.name)
        self.assertEqual(saved.description, self.save_me_1.description)
        self.assertEqual(saved.image_id, self.save_me_1.image_id)

        # Simple check to make sure it can be pulled out of the DB
        found = self.connection.get_resource_categories()
        self.assertEqual(1, len(found))
        self.assertEqual(found[0].id, saved.id)

    def test_save_resource_category_duplicate_name(self):
        # Setup
        self.connection.save_resource_category(self.save_me_1)
        duplicate = models.ResourceCategory(
            name=self.save_me_1.name,
            description='irrelevant',
            image_id='irrelevant'
        )

        # Test
        self.assertRaises(exception.ResourceCategoryExists,
                          self.connection.save_resource_category,
                          duplicate)

    def test_update(self):
        # Setup
        saved = self.connection.save_overcloud(self.save_me_1)

        # Test
        saved.image_id = 'abcdef'
        self.connection.save_overcloud(saved)

        # Verify
        found = self.connection.get_resource_category_by_id(saved.id)
        self.assertEqual(found.image_id, saved.image_id)

    def test_delete_category(self):
        # Setup
        saved = self.connection.save_resource_category(self.save_me_1)

        # Test
        self.connection.delete_resource_category_by_id(saved.id)

        # Verify
        found = self.connection.get_resource_categories()
        self.assertEqual(0, len(found))

    def test_delete_nonexistent_category(self):
        self.assertRaises(exception.ResourceCategoryNotFound,
                          self.connection.delete_resource_category_by_id,
                          'fake-id')

    def test_get_resource_categories(self):
        # Setup
        self.connection.save_resource_category(self.save_me_1)
        self.connection.save_resource_category(self.save_me_2)

        # Test
        all_categories = self.connection.get_resource_categories()

        # Verify
        self.assertEqual(2, len(all_categories))

        found_1 = all_categories[0]
        self.assertEqual(found_1.name, self.save_me_1.name)
        self.assertEqual(found_1.description, self.save_me_1.description)
        self.assertEqual(found_1.image_id, self.save_me_1.image_id)

        found_2 = all_categories[1]
        self.assertEqual(found_2.name, self.save_me_2.name)
        self.assertEqual(found_2.description, self.save_me_2.description)
        self.assertEqual(found_2.image_id, self.save_me_2.image_id)

    def test_get_resource_categories_no_results(self):
        # Test
        all_categories = self.connection.get_resource_categories()

        # Verify
        self.assertTrue(isinstance(all_categories, list))
        self.assertEqual(0, len(all_categories))

    def test_get_resource_category_by_id(self):
        # Setup
        self.connection.save_resource_category(self.save_me_1)
        saved_2 = self.connection.save_resource_category(self.save_me_2)

        # Test
        found = self.connection.get_resource_category_by_id(saved_2.id)

        # Verify
        self.assertTrue(found is not None)
        self.assertEqual(found.id, saved_2.id)
        self.assertEqual(found.name, saved_2.name)

    def test_get_resource_category_by_id_no_result(self):
        self.assertRaises(exception.ResourceCategoryNotFound,
                          self.connection.get_resource_category_by_id,
                          'fake-id')


class OvercloudTests(db_base.DbTestCase):

    def setUp(self):
        super(OvercloudTests, self).setUp()

        self.connection = dbapi.Connection()

        self.attributes_1 = models.OvercloudAttribute(
            key='key-1',
            value='value-1',
        )

        self.attributes_2 = models.OvercloudAttribute(
            key='key-2',
            value='value-2',
        )

        self.overcloud_1 = models.Overcloud(
            name='overcloud-1',
            description='desc-1',
            attributes=[self.attributes_1, self.attributes_2]
        )

        self.overcloud_2 = models.Overcloud(
            name='overcloud-2',
            description='desc-2',
            attributes=[]
        )

    def test_save_overcloud(self):
        # Test
        saved = self.connection.save_overcloud(self.overcloud_1)

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

    def test_save_overcloud_duplicate_name(self):
        # Setup
        self.connection.save_overcloud(self.overcloud_1)
        duplicate = models.Overcloud(
            name=self.overcloud_1.name,
            description='irrelevant',
        )

        # Test
        self.assertRaises(exception.OvercloudExists,
                          self.connection.save_overcloud,
                          duplicate)

    def test_save_overcloud_duplicate_attribute(self):
        # Setup
        duplicate_attribute = models.OvercloudAttribute(
            key=self.attributes_1.key,
            value='irrelevant'
        )
        self.overcloud_1.attributes = [self.attributes_1, duplicate_attribute]

        # Test
        self.assertRaises(exception.DuplicateAttribute,
                          self.connection.save_overcloud,
                          self.overcloud_1)

    def test_delete_overcloud(self):
        # Setup
        saved = self.connection.save_overcloud(self.overcloud_1)

        # Test
        self.connection.delete_overcloud_by_id(saved.id)

        # Verify
        found = self.connection.get_overclouds()
        self.assertEqual(0, len(found))

    def test_delete_nonexistent_overcloud(self):
        self.assertRaises(exception.OvercloudNotFound,
                          self.connection.delete_overcloud_by_id,
                          'irrelevant-id')

    def test_get_overclouds(self):

        # This test also verifies that the attributes are eagerly loaded

        # Setup
        self.connection.save_overcloud(self.overcloud_1)
        self.connection.save_overcloud(self.overcloud_2)

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
        self.connection.save_overcloud(self.overcloud_1)
        saved_2 = self.connection.save_overcloud(self.overcloud_2)

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
