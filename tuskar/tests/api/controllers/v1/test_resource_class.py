from tuskar.api.controllers.v1.types import Rack
from tuskar.api.controllers.v1.types import ResourceClass
from tuskar.common import exception
from tuskar.db.sqlalchemy import api as dbapi
from tuskar.tests.api import api


class TestResourceClasses(api.FunctionalTest):

    db = dbapi.get_backend()

    def setUp(self):
        super(TestResourceClasses, self).setUp()
        self.rc = self.db.create_resource_class(ResourceClass(
            name='test resource class',
            service_type='compute',
            image_id='58f950f7-215b-455a-81c4-1fce9f395109'
        ))
        self.addCleanup(self.db.delete_resource_class, self.rc.id)

        self.racks = []
        self.addCleanup(self.teardown_racks)

    def setup_racks(self):
        for rack_num in range(1, 4):
            self.racks.append(self.db.create_rack(Rack(
                name='rack no. {0}'.format(rack_num),
                subnet='192.168.1.{0}/24'.format(rack_num))
            ))

    def teardown_racks(self):
        for rack in self.racks:
            self.db.delete_rack(rack.id)

    @staticmethod
    def sorted_ids(resources):
        if resources and hasattr(resources[0], 'id'):
            return sorted([r.id for r in resources])
        else:
            return sorted([r['id'] for r in resources])

    def assert_racks_present(self, sent_json, response):
        self.assertEqual(self.sorted_ids(sent_json['racks']),
                         self.sorted_ids(response.json['racks']))
        updated_rc = self.db.get_resource_class(self.rc.id)
        self.assertEqual(self.sorted_ids(sent_json['racks']),
                         self.sorted_ids(updated_rc.racks))

    def test_list_resource_classes(self):
        response = self.get_json('/resource_classes/', expect_errors=True)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json), 1)
        row = response.json[0]
        self.assertEqual(row['name'], 'test resource class')

    def test_get_resource_class(self):
        rc_id = '1'
        # without expect_errors, the response type is a list
        response = self.get_json('/resource_classes/' + rc_id,
                                 expect_errors=True)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['name'], 'test resource class')

    def test_create_resource_class(self):
        json = {
            'name': 'new',
            'service_type': 'compute',
            'image_id': 'f815a5d4-2b46-4e3b-afd0-a740d3cff49c',
        }
        response = self.post_json('/resource_classes/', params=json)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['name'], json['name'])
        row = self.db.get_resource_class(response.json['id'])
        self.assertEqual(row.name, json['name'])
        self.assertEqual(row.image_id, json['image_id'])

    def test_create_resource_class_default_image_id(self):
        json = {
            'name': 'new',
            'service_type': 'compute',
        }
        response = self.post_json('/resource_classes/', params=json)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['name'], json['name'])
        row = self.db.get_resource_class(response.json['id'])
        self.assertEqual(row.name, json['name'])

    def test_update_name_only(self):
        json = {'name': 'updated name'}
        response = self.put_json('/resource_classes/' + str(self.rc.id),
                                 params=json, status=200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['name'], json['name'])
        updated_rc = self.db.get_resource_class(self.rc.id)
        self.assertEqual(updated_rc.name, json['name'])

    def test_update_racks(self):
        self.setup_racks()
        # Assign racks for the first time
        json = {'racks': [{'id': self.racks[0].id},
                          {'id': self.racks[1].id}]}
        response = self.put_json('/resource_classes/' + str(self.rc.id),
                                 params=json, status=200)
        self.assert_racks_present(json, response)

        # Re-assign racks: remove one, keep one, add one new
        json = {'racks': [{'id': self.racks[1].id},
                          {'id': self.racks[2].id}]}
        response = self.put_json('/resource_classes/' + str(self.rc.id),
                                 params=json, status=200)
        self.assert_racks_present(json, response)

    def test_delete_resource_class(self):
        rc_id = '1'
        response = self.delete_json('/resource_classes/' + rc_id)
        self.assertRaises(exception.ResourceClassNotFound,
                          self.db.get_resource_class, rc_id)
