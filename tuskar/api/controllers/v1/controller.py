#from oslo.config import cfg
import pecan
#from pecan.core import render
#from pecan import rest
#import wsme
#from wsme import api
#from wsme import types as wtypes
#import wsmeext.pecan as wsme_pecan

#from tuskar.common import exception
#from tuskar.openstack.common import log

from tuskar.api.controllers.v1.data_center import DataCenterController
from tuskar.api.controllers.v1.node import NodesController
from tuskar.api.controllers.v1.overcloud import OvercloudsController
from tuskar.api.controllers.v1.rack import RacksController
from tuskar.api.controllers.v1.resource_class import ResourceClassesController


class Controller(object):
    """Version 1 API controller root."""

    racks = RacksController()
    resource_classes = ResourceClassesController()
    data_centers = DataCenterController()
    overclouds = OvercloudsController()
    nodes = NodesController()

    @pecan.expose('json')
    def index(self):
        return {
            'version': {
                'status': 'stable',
                'media-types': [{'base': 'application/json'}],
                'id': 'v1.0',
                'links': [{
                    'href': '/v1/',
                    'rel': 'self',
                }]
            }
        }
