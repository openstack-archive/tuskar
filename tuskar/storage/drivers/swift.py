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

from StringIO import StringIO

from tuskar.openstack.common import log as logging
from tuskar.storage.drivers.base import BaseDriver
from tuskar.storage.models import StoredFile

_LOG = logging.getLogger('tuskar.storage.drivers.swift')


class SwiftDriver(BaseDriver):

    def _str_to_stringio(self, str_contents):
        sio = StringIO()
        sio.write(str_contents)
        return sio

    def _create_model(self, store, headers, contents):
        return StoredFile()

    def __init__(self, client):
        self.client = client

    def create(self, store, filename, contents):
        contents_io = self._str_to_stringio(contents)
        self.client.put_object(store.object_type, filename, contents_io)
        headers = self.client.head_object(filename)

        return self._create_model(store, headers, contents)

    def retrieve(self, store, uuid):
        headers, contents = self.client.get_object(store.object_type, uuid)
        return self._create_model(store, headers, contents)

    def update(self, store, uuid, filename, contents):
        assert uuid == filename
        self.create(store.object_type, uuid, contents)

    def delete(self, store, uuid):
        self.client.delete(store.object_type, uuid)

    def list(self, store):
        _, swift_objects = self.client.get_container(store.object_type)
        return [self._create_model(store, None, obj) for obj in swift_objects]

    def retrieve_by_name(self, store, name, version=None):

        if version is not None:
            _LOG.warn("Version is not supported by the Swift backend")

        return self.retrieve(store, name)
