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

import pecan

from tuskar.api.controllers.v2.plans import PlansController
from tuskar.api.controllers.v2.roles import RolesController


class Controller(object):
    """Version 2 API controller root."""

    plans = PlansController()
    roles = RolesController()

    @pecan.expose('json')
    def index(self):
        return {
            'version': {
                'status': 'development',
                'media-types': [{'base': 'application/json'}],
                'id': 'v2.0',
                'links': [{
                    'href': '/v2/',
                    'rel': 'self',
                }]
            }
        }
