# Copyright (c) 2013 Mirantis
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
        rack1 = utils.get_test_rack(
            name='rack_with_nodes', nodes=True,
            resource_class=True, rc_id=self.db_rc.id)
        self.rack1 = self.db.create_rack(rack1)

    def tearDown(self):
        # import pdb; pdb.set_trace()
        self.db.delete_resource_class(self.db_rc.id)
        self.db.delete_rack(self.rack1.id)
        super(TestDbTuskarNodes, self).tearDown()

    def test_node_get_success(self):
        self.db.get_node(self.rack1.nodes[0].id)

    def test_node_get_not_found(self):
        self.assertRaises(exception.NodeNotFound, self.db.get_node, 777)
