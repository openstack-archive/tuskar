from tuskar.api.controllers.v1.types import Capacity
from tuskar.api.controllers.v1.types import Chassis
from tuskar.api.controllers.v1.types import Node
from tuskar.api.controllers.v1.types import Rack
from tuskar.api.controllers.v1.types import ResourceClass
from tuskar.db.sqlalchemy import api as dbapi
from tuskar.tests.api import api


class TestRacks(api.FunctionalTest):

    test_rack = None
    db = dbapi.get_backend()

    def valid_rack_json(self, rack_json, test_rack=None):
        rack = None

        if test_rack is None:
            rack = self.test_rack
        else:
            rack = test_rack

        self.assertEqual(rack_json['id'], rack.id)
        self.assertEqual(rack_json['name'], rack.name)
        self.assertEqual(rack_json['slots'], rack.slots)
        self.assertEqual(rack_json['subnet'], rack.subnet)
        self.assertTrue(rack_json['nodes'])
        self.assertEqual(rack_json['nodes'][0]['id'],
                         str(rack.nodes[0].id))
        self.assertTrue(rack_json['capacities'])
        self.assertEqual(rack_json['capacities'][0]['name'],
                         rack.capacities[0].name)
        self.assertEqual(rack_json['capacities'][0]['value'],
                         rack.capacities[0].value)
        self.assertTrue(rack_json['links'])
        self.assertEqual(rack_json['links'][0]['rel'], 'self')
        self.assertEqual(rack_json['links'][0]['href'],
                         'http://localhost/v1/racks/' + str(rack.id))

    def setUp(self):
        """Create 'test_rack'."""

        super(TestRacks, self).setUp()
        self.test_resource_class = None
        self.test_rack = self.db.create_rack(
            Rack(name='test-rack',
                 slots=1,
                 subnet='10.0.0.0/24',
                 location='nevada',
                 chassis=Chassis(id='123'),
                 capacities=[Capacity(name='cpu', value='10',
                                      unit='count')],
                 nodes=[Node(id='1')]
                 ))
        # FIXME: For some reason the 'self.test_rack' does not
        #        lazy-load the 'nodes' and other attrs when
        #        having more than 1 test method...
        #
        self.test_rack = self.db.get_rack(self.test_rack.id)

    def tearDown(self):
        self.db.delete_rack(self.test_rack.id)
        if self.test_resource_class:
            self.db.delete_resource_class(self.test_resource_class.id)
        super(TestRacks, self).tearDown()

    def setup_resource_class(self):
        if not self.test_resource_class:
            self.test_resource_class = self.db.create_resource_class(
                ResourceClass(
                    name='test resource class',
                    service_type='compute',
                    image_id='694327d9-6cf0-4bed-bb5d-7456f34cf1ff',
                ))

    def test_it_returns_single_rack(self):
        response = self.get_json('/racks/' + str(self.test_rack.id),
                                 expect_errors=True)

        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, "application/json")
        self.valid_rack_json(response.json)

    def test_it_returns_rack_list(self):
        response = self.get_json('/racks', expect_errors=True)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, "application/json")

        # The 'test_rack' is present in the racks listing:
        rack_json = filter(lambda r: r['id'] == self.test_rack.id,
                           response.json)
        self.assertEqual(len(rack_json), 1)

        # And the Rack serialization is correct
        self.valid_rack_json(rack_json[0])

    def test_it_updates_rack(self):
        json = {
            'name': 'blabla',
        }
        response = self.put_json('/racks/' + str(self.test_rack.id),
                                 params=json, status=200)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json['name'], json['name'])
        updated_rack = self.db.get_rack(self.test_rack.id)
        self.assertEqual(updated_rack.name, json['name'])

    def test_it_allow_to_update_rack_state(self):
        json = {
            'state': 'active',
        }
        response = self.put_json('/racks/' + str(self.test_rack.id),
                                 params=json, status=200)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json['state'], json['state'])
        updated_rack = self.db.get_rack(self.test_rack.id)
        self.assertEqual(updated_rack.state, json['state'])

    def test_it_not_allow_to_update_rack_state_with_unknown_state(self):
        json = {
            'state': 'trololo',
        }
        response = self.put_json('/racks/' + str(self.test_rack.id),
                                 params=json, status=200)
        self.assertEqual(response.content_type, "application/json")
        self.assertNotEqual(response.json['state'], json['state'])
        updated_rack = self.db.get_rack(self.test_rack.id)
        self.assertNotEqual(updated_rack.state, json['state'])

    def test_it_creates_and_deletes_new_rack(self):
        json = {
            'name': 'test-rack-create',
            'subnet': '127.0.0./24',
            'slots': '10',
            'location': 'texas',
            'capacities': [
                {'name': 'memory', 'value': '1024', 'unit': 'MB'}
            ],
            'nodes': [
                {'id': '1234567'},
                {'id': '7891011'}
            ]
        }
        response = self.post_json('/racks', params=json, status=201)
        self.assertEqual(response.content_type, "application/json")

        self.assertTrue(response.json['id'])
        self.assertEqual(response.json['name'], json['name'])

        self.assertEqual(response.json['state'], 'unprovisioned')

        self.assertEqual(str(response.json['slots']), json['slots'])
        self.assertEqual(str(response.json['location']), json['location'])
        self.assertEqual(response.json['subnet'], json['subnet'])
        self.assertEqual(len(response.json['nodes']), 2)
        self.assertEqual(str(response.json['capacities'][0]['unit']), 'MB')

        # Make sure we delete the Rack we just created
        self.db.delete_rack(response.json['id'])

    def test_it_returns_404_when_getting_unknown_rack(self):
        response = self.get_json('/racks/unknown',
                                 expect_errors=True,
                                 headers={"Accept": "application/json"}
                                 )

        self.assertEqual(response.status_int, 404)

    # FIXME(mfojtik): This test will fail because of Pecan bug, see:
    # https://github.com/tuskar/tuskar/issues/18
    #
    def test_it_returns_404_when_deleting_unknown_rack(self):
        response = self.delete_json('/racks/unknown',
                                    expect_errors=True,
                                    headers={"Accept": "application/json"}
                                    )

        self.assertEqual(response.status_int, 404)

    # this is test for https://github.com/tuskar/tuskar/issues/39
    def test_it_updates_resource_class_id_when_already_present(self):
        # create needed resource_class
        self.setup_resource_class()

        # update precreated rack with resource_class_id for test
        rack_update_json = {
            'resource_class': {
                'id': self.test_resource_class.id
            }
        }
        first_update_response = self.put_json(
            '/racks/' + str(self.test_rack.id),
            rack_update_json)
        self.assertEqual(first_update_response.status_int, 200)
        self.assertEqual(first_update_response.json['resource_class']['id'],
                         rack_update_json['resource_class']['id'])

        # repeat update of rack - simulates updating resource_class_id when
        # already present
        second_update_response = self.put_json(
            '/racks/' + str(self.test_rack.id),
            rack_update_json)
        self.assertEqual(second_update_response.status_int, 200)
        self.assertEqual(second_update_response.json['resource_class']['id'],
                         rack_update_json['resource_class']['id'])
