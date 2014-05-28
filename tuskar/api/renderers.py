# Copyright 2013 Red Hat, Inc.
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

import pecan
import wsme
from wsme import api


class JSONRenderer(object):
    """Custom JSON renderer.

    Renders to JSON and handles responses for various HTTP status codes.
    """

    def __init__(self, path, extra_vars):
        """Create an empty __init__ to accept the arguments provided to a
        Renderer but ignore them as they are not needed.
        """

    def _render_fault(self, message, details, code=500):
        """Given the namespace dictionary render a JSON error response for the
        fault in the format defined by the OpenStack identity service
        documentation.
        """

        body = {
            'identityFault': {
                "message": message,
                "details": details,
                "code": code
            }
        }
        return wsme.rest.json.encode_error(None, body)

    def render(self, template_path, namespace):
        """Given a namespace dict render the response as JSON and return.

        If the dict contains a faultcode or wsme.api.Response its a fault from
        user code and is rendered via _render_fault.

        template_path is a required parameter for renderers but unused in
        this context.
        """

        if 'faultcode' in namespace:
            return self._render_fault(
                namespace['faultstring'],
                namespace['debuginfo'])

        result = namespace['result']
        if isinstance(namespace['result'], api.Response):
            pecan.response.status_code = result.status_code
            return self._render_fault(
                result.obj.faultstring, result.obj.debuginfo,
                code=result.status_code)

        return wsme.rest.json.encode_result(
            result,
            namespace['datatype']
        )
