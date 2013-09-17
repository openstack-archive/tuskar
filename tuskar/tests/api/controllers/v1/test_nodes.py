from tuskar.api.controllers.v1.types import Capacity
from tuskar.api.controllers.v1.types import Chassis
from tuskar.api.controllers.v1.types import Node
from tuskar.api.controllers.v1.types import Rack
from tuskar.db.sqlalchemy import api as dbapi
from tuskar.tests.api import api


class TestNodes(api.FunctionalTest):

    test_node = None
    db = dbapi.get_backend()

    def setUp(self):
        """Create 'test_rack'."""

        super(TestNodes, self).setUp()
        # self.test_resource_class = None
        self.test_node = Node(id='1', name='test_node', node_id='1')
        self.test_rack = self.db.create_rack(
            Rack(name='test-rack',
                 slots=1,
                 subnet='10.0.0.0/24',
                 location='nevada',
                 chassis=Chassis(id='123'),
                 capacities=[Capacity(name='cpu', value='10',
                                      unit='count')],
                 nodes=[self.test_node]
                 ))

    def tearDown(self):
        self.db.delete_rack(self.test_rack.id)
        super(TestNodes, self).tearDown()

    def valid_node_json(self, node_json, test_node=None):
        node = self.test_node if test_node is None else test_node

        self.assertEqual(node_json['nova_baremetal_node_id'], node.node_id)
        self.assertEqual(node_json['id'], node.id)

    def test_it_returns_single_node(self):
        response = self.get_json('/nodes/' + str(self.test_node.id),
                                 expect_errors=True)

        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.valid_node_json(response.json)

        # it should contain a rack
        rack = response.json['rack']
        self.assertEqual(rack['id'], self.test_rack.id)

    def test_it_returns_node_list(self):
        response = self.get_json('/nodes/', expect_errors=True)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        # It should consist solely of one node:
        self.assertEqual(len(response.json), 1)

        # And that node should pass our JSON test:
        self.valid_node_json(response.json[0])
