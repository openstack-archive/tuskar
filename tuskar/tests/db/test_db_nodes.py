# Copyright 2013 Mirantis Inc.
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


class TestDbTuskarNodes(db_base.DbTestCase):

    def setUp(self):
        super(TestDbTuskarNodes, self).setUp()
        self.db = dbapi.get_backend()
        rc1 = utils.get_test_resource_class(name='rc1', type='compute')
        self.db_rc = self.db.create_resource_class(rc1)
        self.addCleanup(self.db.delete_resource_class, self.db_rc.id)

        rack1 = utils.get_test_rack(
            name='rack_with_nodes', nodes=True,
            resource_class=True, rc_id=self.db_rc.id)
        self.rack1 = self.db.create_rack(rack1)
        self.addCleanup(self.db.delete_rack, self.rack1.id)

    def test_node_get_success(self):
        rack_node = self.rack1.nodes[0]
        db_node = self.db.get_node(rack_node.id)
        self.assertEqual(db_node.as_dict(), rack_node.as_dict())

    def test_node_get_not_found(self):
        self.assertRaises(exception.NodeNotFound, self.db.get_node, 777)
