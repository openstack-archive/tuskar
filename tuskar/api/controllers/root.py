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

from tuskar.api.controllers.v1 import controller as v1_controller
from tuskar.api.controllers.v2 import controller as v2_controller


class RootController(object):

    v1 = v1_controller.Controller()
    v2 = v2_controller.Controller()

    @pecan.expose('json')
    def index(self):
        return {
            'versions': {
                'values': [
                    {
                        'status': 'development',
                        'media-types': [{'base': 'application/json'}],
                        'id': 'v1.0',
                        'links': [{
                            'href': '/v1/',
                            'rel': 'self',
                        }]
                    },
                    {
                        'status': 'development',
                        'media-types': [{'base': 'application/json'}],
                        'id': 'v2.0',
                        'links': [{
                            'href': '/v2/',
                            'rel': 'self',
                        }]
                    }
                ]
            }
        }
