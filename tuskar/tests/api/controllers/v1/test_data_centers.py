import uuid

from tuskar.api.controllers.v1.types import Node
from tuskar.api.controllers.v1.types import Rack
from tuskar.api.controllers.v1.types import Relation
from tuskar.api.controllers.v1.types import ResourceClass
from tuskar.db.sqlalchemy import api as dbapi
from tuskar.tests.api import api


class TestDataCenters(api.FunctionalTest):

    db = dbapi.get_backend()

    # Setup an ResourceClass with some Rack to trigger also bash script
    # generation and to add some Racks into the Heat template
    #
    def setUp(self):
        super(TestDataCenters, self).setUp()
        self.rc = self.db.create_resource_class(ResourceClass(
            name='t1',
            service_type='compute',
            image_id='a2822b68-6d8e-44be-8861-1065d6df99a6',
        ))
        self.racks = []

    def tearDown(self):
        self.db.delete_resource_class(self.rc.id)
        self.teardown_racks()
        super(TestDataCenters, self).tearDown()

    def setup_racks(self):
        for rack_num in range(1, 4):
            self.racks.append(self.db.create_rack(Rack(
                name='rack-no-{0}'.format(rack_num),
                subnet='192.168.2.{0}/24'.format(rack_num),
                resource_class=Relation(id=self.rc.id),
                nodes=[Node(id=str(uuid.uuid4())), Node(id=str(uuid.uuid4()))]
            ))
            )

    def teardown_racks(self):
        for rack in self.racks:
            self.db.delete_rack(rack.id)

    def test_it_returns_the_heat_overcloud_template(self):
        self.setup_racks()
        response = self.app.get('/v1/data_centers/template')
        self.assertEqual(response.status, '200 OK')
        self.assertRegexpMatches(response.body, 'HeatTemplateFormatVersion')
