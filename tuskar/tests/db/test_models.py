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

import unittest

from tuskar.db.sqlalchemy import models


class OvercloudRoleTests(unittest.TestCase):

    def test_equal(self):
        # Setup
        res_cat_1 = models.OvercloudRole(name='foo')
        res_cat_2 = models.OvercloudRole(name='foo')

        # Test
        self.assertTrue(res_cat_1 == res_cat_2)

    def test_not_equal(self):
        # Setup
        res_cat_1 = models.OvercloudRole(name='foo')
        res_cat_2 = models.OvercloudRole(name='bar')

        # Test
        self.assertTrue(res_cat_1 != res_cat_2)


class OvercloudRoleCountTests(unittest.TestCase):

    def test_equal(self):
        # Setup
        count_1 = models.OvercloudRoleCount(overcloud_id='o1',
                                            overcloud_role_id='r1')
        count_2 = models.OvercloudRoleCount(overcloud_id='o1',
                                            overcloud_role_id='r1')

        # Test
        self.assertTrue(count_1 == count_2)

    def test_same_overcloud_different_role(self):
        # Setup
        count_1 = models.OvercloudRoleCount(overcloud_id='o1',
                                            overcloud_role_id='r1')
        count_2 = models.OvercloudRoleCount(overcloud_id='o1',
                                            overcloud_role_id='r2')

        # Test
        self.assertTrue(count_1 != count_2)

    def test_different_overcloud_same_role(self):
        # Setup
        count_1 = models.OvercloudRoleCount(overcloud_id='o1',
                                            overcloud_role_id='r1')
        count_2 = models.OvercloudRoleCount(overcloud_id='o2',
                                            overcloud_role_id='r1')

        # Test
        self.assertTrue(count_1 != count_2)


class OvercloudTests(unittest.TestCase):

    def test_equal(self):
        # Setup
        overcloud_1 = models.Overcloud(name='foo')
        overcloud_2 = models.Overcloud(name='foo')

        # Test
        self.assertTrue(overcloud_1 == overcloud_2)

    def test_not_equal(self):
        # Setup
        overcloud_1 = models.Overcloud(name='foo')
        overcloud_2 = models.Overcloud(name='bar')

        # Test
        self.assertTrue(overcloud_1 != overcloud_2)


class OvercloudAttributesTests(unittest.TestCase):

    def test_equal(self):
        # Setup
        attr_1 = models.OvercloudAttribute(overcloud_id='foo', key='bar')
        attr_2 = models.OvercloudAttribute(overcloud_id='foo', key='bar')

        # Test
        self.assertTrue(attr_1 == attr_2)

    def test_same_overcloud_different_key(self):
        # Setup
        attr_1 = models.OvercloudAttribute(overcloud_id='foo', key='bar')
        attr_2 = models.OvercloudAttribute(overcloud_id='foo', key='rab')

        # Test
        self.assertTrue(attr_1 != attr_2)

    def test_different_overcloud_same_key(self):
        # Setup
        attr_1 = models.OvercloudAttribute(overcloud_id='oof', key='bar')
        attr_2 = models.OvercloudAttribute(overcloud_id='foo', key='bar')

        # Test
        self.assertTrue(attr_1 != attr_2)
