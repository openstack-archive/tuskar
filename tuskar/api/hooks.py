# -*- encoding: utf-8 -*-
#
# Copyright © 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import re
import wsme

from oslo.config import cfg
from pecan import hooks

from tuskar.db import api as dbapi


class ConfigHook(hooks.PecanHook):
    """Attach the configuration object to the request
    so controllers can get to it.
    """

    def before(self, state):
        state.request.cfg = cfg.CONF


class DBHook(hooks.PecanHook):

    def before(self, state):
        state.request.dbapi = dbapi.get_instance()        

class ValidatePatchHook(hooks.PecanHook):
    """Ensures the PATCH request body is correctly formed"""

    path_regexpr = re.compile("^/[a-zA-Z0-9-_]+(/[a-zA-Z0-9-_]+)*$")
    supported_operations = ["replace"]

    def before(self, state):
        if state.request.method.upper() == 'PATCH':
            self.validate_patch(state.request.body)

    def validate_patch(self, patch):
        patch = json.loads(patch)
        errors = []

        # Instead of checking this manually maybe we can use JSON Schema
        for p in patch:
            if not isinstance(p, dict):
                errors.append("Invalid patch line format: %s" % str(p))
            else:
                if not set(["path", "op"]).issubset(set(p.keys())):
                    errors.append("Invalid patch line: %s" % str(p))

                if p["op"] not in self.supported_operations:
                    errors.append("Operation not supported: %s" % p["op"])

                if not self.path_regexpr.match(p["path"]):
                    errors.append("Invalid path: %s" % p["path"])

        if errors:
            raise wsme.exc.ClientSideError(",".join(errors))