# vim: tabstop=4 shiftwidth=4 softtabstop=4
# -*- encoding: utf-8 -*-
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

import json

import pecan
import wsme
from wsme import api


class JSonRenderer(object):
    """Custom json renderer.

    Renders to json and handles responses for various HTTP status codes.
    """
    def __init__(self, path, extra_vars):
        pass

    def render(self, template_path, namespace):
        if 'faultcode' in namespace:
            return wsme.rest.json.encode_error(None, namespace)

        result = namespace['result']
        if isinstance(namespace['result'], api.Response):
            pecan.response.status_code = result.status_code
            val = json.dumps({'faultstring': result.obj.faultstring,
                              'faultcode': result.obj.faultcode})
            return val

        return wsme.rest.json.encode_result(
            namespace['result'],
            namespace['datatype']
        )
