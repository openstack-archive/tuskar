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

import testtools
from wsme import types as wtypes

from tuskar.api.controllers.v1 import models as api_models
from tuskar.db.sqlalchemy import models as db_models


class BaseTests(testtools.TestCase):

    def test_lookup(self):
        # Setup
        class Stub(api_models.Base):
            a1 = int
            a2 = int

        stub = Stub(a1=1, a2=wtypes.Unset)

        # Test
        self.assertEqual(1, stub._lookup('a1'))
        self.assertIsNone(stub._lookup('a2'))


class OvercloudModelTests(testtools.TestCase):

    def test_from_db_model(self):
        # Setup
        db_attrs = [
            db_models.OvercloudAttribute(
                id=10,
                overcloud_id=1,
                key='key-1',
                value='value-1',
            ),
            db_models.OvercloudAttribute(
                id=20,
                overcloud_id=1,
                key='key-2',
                value='value-2',
            ),
        ]

        db_counts = [
            db_models.OvercloudRoleCount(
                id=100,
                overcloud_id=1,
                overcloud_role_id=5,
                num_nodes=5,
            )
        ]

        db_model = db_models.Overcloud(
            id=1,
            stack_id='stack-1',
            name='name-1',
            description='desc-1',
            attributes=db_attrs,
            counts=db_counts,
        )

        # Test
        api_model = api_models.Overcloud.from_db_model(db_model)

        # Verify
        self.assertTrue(api_model is not None)
        self.assertTrue(isinstance(api_model, api_models.Overcloud))

        self.assertEqual(api_model.id, db_model.id)
        self.assertEqual(api_model.stack_id, db_model.stack_id)
        self.assertEqual(api_model.name, db_model.name)
        self.assertEqual(api_model.description, db_model.description)

        self.assertEqual(len(api_model.attributes), len(db_model.attributes))
        self.assertTrue(isinstance(api_model.attributes, dict))
        for d_attr in db_model.attributes:
            self.assertEqual(api_model.attributes[d_attr.key], d_attr.value)

        self.assertEqual(len(api_model.counts), len(db_model.counts))
        for a_count, d_count in zip(api_model.counts, db_model.counts):
            self.assertTrue(isinstance(a_count,
                                       api_models.OvercloudRoleCount))
            self.assertEqual(a_count.id, d_count.id)
            self.assertEqual(a_count.overcloud_role_id,
                             d_count.overcloud_role_id)
            self.assertEqual(a_count.overcloud_id, d_count.overcloud_id)
            self.assertEqual(a_count.num_nodes, d_count.num_nodes)

    def test_to_db_model(self):
        # Setup
        api_attrs = {'key-1': 'value-1'}

        api_counts = [
            api_models.OvercloudRoleCount(
                id=10,
                overcloud_role_id=2,
                num_nodes=50,
            ),
            api_models.OvercloudRoleCount(
                id=11,
                overcloud_role_id=3,
                num_nodes=15,
            ),
        ]

        api_model = api_models.Overcloud(
            id=1,
            stack_id='stack-1',
            name='name-1',
            description='desc-1',
            attributes=api_attrs,
            counts=api_counts,
        )

        # Test
        db_model = api_model.to_db_model()

        # Verify
        self.assertTrue(db_model is not None)
        self.assertTrue(isinstance(db_model, db_models.Overcloud))
        self.assertEqual(db_model.id, api_model.id)
        self.assertEqual(db_model.stack_id, api_model.stack_id)
        self.assertEqual(db_model.name, api_model.name)
        self.assertEqual(db_model.description, api_model.description)

        self.assertEqual(len(db_model.attributes), len(api_model.attributes))
        for d_attr in db_model.attributes:
            self.assertTrue(isinstance(d_attr, db_models.OvercloudAttribute))
            self.assertEqual(d_attr.overcloud_id, api_model.id)
            self.assertEqual(d_attr.value, api_attrs[d_attr.key])

        self.assertEqual(len(db_model.counts), len(api_model.counts))
        for d_count, a_count in zip(db_model.counts, api_model.counts):
            self.assertTrue(isinstance(d_count,
                                       db_models.OvercloudRoleCount))
            self.assertEqual(d_count.overcloud_role_id,
                             a_count.overcloud_role_id)
            self.assertEqual(d_count.overcloud_id, api_model.id)
            self.assertEqual(d_count.num_nodes, a_count.num_nodes)
