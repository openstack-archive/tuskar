import pecan
from pecan import rest

import wsmeext.pecan as wsme_pecan

from tuskar.api.controllers.v1.types import Error
from tuskar.api.controllers.v1.types import Node
from tuskar.common import exception
from tuskar.openstack.common import log
from wsme import api

LOG = log.getLogger(__name__)


class NodesController(rest.RestController):
    """REST controller for Node."""

    @wsme_pecan.wsexpose([Node])
    def get_all(self):
        """Retrieve a list of all nodes."""
        result = []
        db_api = pecan.request.dbapi

        for node in db_api.get_nodes(None):
            result.append(Node.convert(node))

        return result

    @wsme_pecan.wsexpose(Node, unicode)
    def get_one(self, node_id):
        """Retrieve an instance of a Node."""
        db_api = pecan.request.dbapi

        try:
            node = db_api.get_node(node_id)
        except exception.TuskarException as e:
            response = api.Response(None,
                                    error=Error(faultcode=e.code,
                                                faultstring=str(e)),
                                    status_code=e.code)
            return response
        return Node.convert(node)
