#from tuskar.api.controllers.v1.types import Node
#from tuskar.api.controllers.v1.types import Rack
#from tuskar.api.controllers.v1.types import Relation
from tuskar.api.controllers.v1.types import ResourceClass
from tuskar.db.sqlalchemy import api as dbapi
from tuskar.tests.api import api


class TestFlavors(api.FunctionalTest):

    db = dbapi.get_backend()

    # create a test resource class
    def setUp(self):
        super(TestFlavors, self).setUp()
        self.rc = self.db.create_resource_class(ResourceClass(
            name='flavor_test_resource_class',
            service_type='compute',
            image_id='3b242fc2-4972-434c-9fc6-2885981e2236',
        ))
        self.addCleanup(self.db.delete_resource_class, self.rc.id)

    def test_it_can_create_and_delete_a_flavor(self):
        # create a flavor and inspect response
        request_json = {
            'name': 'test_flavor',
            'max_vms': '10',
            'capacities': [
                {'name': 'memory', 'value': '1024', 'unit': 'MB'},
                {'name': 'cpu', 'value': '2', 'unit': 'count'},
                {'name': 'storage', 'value': '1024', 'unit': 'GB'},
            ]}
        response = self.post_json('/resource_classes/' + str(self.rc.id) +
                                  '/flavors', params=request_json, status=201)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(response.json['id'])
        self.assert_equality(request_json, response.json, ['name', 'max_vms'])
        flav_id = response.json['id']
        # delete the flavor
        response = self.delete_json('/resource_classes/' + str(self.rc.id) +
                                    '/flavors/' + str(flav_id), status=204)

    def test_it_can_update_a_flavor(self):
        # first create the flavor
        request_json = {
            'name': 'test_flavor',
            'max_vms': '10',
            'capacities': [
                {'name': 'memory', 'value': '1024', 'unit': 'MB'},
                {'name': 'cpu', 'value': '2', 'unit': 'count'},
                {'name': 'storage', 'value': '1024', 'unit': 'GB'},
            ]}
        response = self.post_json('/resource_classes/' + str(self.rc.id) +
                                  '/flavors', params=request_json, status=201)
        self.assert_equality(request_json, response.json, ['name', 'max_vms'])
        flav_id = response.json['id']
        # now update it:
        update_json = {
            'name': 'update_test_flavor',
            'max_vms': '11',
            'capacities': [
                {'name': 'memory', 'value': '1111', 'unit': 'MB'},
                {'name': 'cpu', 'value': '44', 'unit': 'count'},
                {'name': 'storage', 'value': '2222', 'unit': 'GB'},
            ]}
        update_response = self.put_json(
            '/resource_classes/' + str(self.rc.id) +
            '/flavors/' + str(flav_id),
            params=update_json,
            status=200)
        self.assert_equality(update_json,
                             update_response.json,
                             ['name', 'max_vms'])
        self.assertEqual(update_response.json['id'], flav_id)
        for c in update_response.json['capacities']:
            if c['name'] == 'memory':
                self.assertEqual(c['value'], '1111')
            elif c['name'] == 'cpu':
                self.assertEqual(c['value'], '44')
            elif c['name'] == 'storage':
                self.assertEqual(c['value'], '2222')
        # delete
        response = self.delete_json('/resource_classes/' + str(self.rc.id) +
                                    '/flavors/' + str(flav_id), status=204)

    def test_it_can_replace_resource_class_flavors(self):
        # first create flavor:
        request_json = {
            'name': 'test_flavor',
            'max_vms': '10',
            'capacities': [
                {'name': 'memory', 'value': '1024', 'unit': 'MB'},
                {'name': 'cpu', 'value': '2', 'unit': 'count'},
                {'name': 'storage', 'value': '1024', 'unit': 'GB'},
            ]}
        response = self.post_json('/resource_classes/' + str(self.rc.id) +
                                  '/flavors', params=request_json, status=201)
        self.assert_equality(request_json, response.json, ['name', 'max_vms'])
        flav_id = response.json['id']
        # now replace flavors with new ones:
        replace_json = {"flavors": [
            {'name': 'flavor1',
             'max_vms': '1',
             'capacities': [
                 {'name': 'memory', 'value': '1', 'unit': 'MB'},
                 {'name': 'cpu', 'value': '1', 'unit': 'count'},
                 {'name': 'storage', 'value': '1', 'unit': 'GB'}]},
            {'name': 'flavor2',
             'max_vms': '2',
             'capacities': [
                 {'name': 'memory', 'value': '2', 'unit': 'MB'},
                 {'name': 'cpu', 'value': '2', 'unit': 'count'},
                 {'name': 'storage', 'value': '2', 'unit': 'GB'}]}]}
        update_response = self.put_json('/resource_classes/' + str(self.rc.id),
                                        params=replace_json, status=200)
        self.assertEqual(response.content_type, "application/json")
        for flav in update_response.json['flavors']:
            self.assertTrue(flav['name'] in ['flavor1', 'flavor2'])
            self.assertTrue(str(flav['max_vms']) in ['1', '2'])
            for c in flav['capacities']:
                self.assertTrue(c['value'] in ['1', '2'])

    def assert_equality(self, req_json, res_json, values):
        for val in values:
            # if type(req_json[val]) == 'str':
            self.assertEqual(str(req_json[val]), str(res_json[val]))
            # elif type(req_json[val]) == 'list':
            #  self.assert_equality(req_json[val], res_json[val],
