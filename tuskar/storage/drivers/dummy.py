# -*- encoding: utf-8 -*-
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

from tuskar.storage.drivers.base import BaseDriver

from sys import stdout


class DummyDriver(BaseDriver):

    def __init__(self, client, out=stdout):
        self.client = client
        self.out = out

    def _log(self, msg):
        self.out.write(msg)

    def create(self, object_type, filename, contents):
        self._log("Creating {0} named {1}".format(object_type, filename))
        return self.client.create(object_type, filename, contents)

    def retrieve(self, object_type, uuid):
        self._log("Retrieving {0} with ID {1}".format(object_type, uuid))
        return self.client.retrieve(object_type, uuid)

    def update(self, object_type, uuid, filename, contents):
        self._log("Updating {0} with ID {1}".format(object_type, uuid))
        return self.client.update(object_type, uuid, filename, contents)

    def delete(self, object_type, uuid):
        self._log("Deleting {0} with ID {1}".format(object_type, uuid))
        self.client.delete(object_type, uuid)

    def list(self, object_type):
        self._log("Listing {0}".format(object_type))
        self.client.list(object_type)

    def retrieve_by_name(self, object_type, name, version=None):
        pass
