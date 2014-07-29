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

from abc import ABCMeta

from six import add_metaclass


@add_metaclass(ABCMeta)
class _BaseStore(object):

    object_type = None

    def __init__(self, driver):
        self._driver = driver

    def create(self, contents):
        return self._driver.create(self, None, contents)

    def update(self, uuid, contents):
        return self._driver.update(self, uuid, None, contents)

    def retrieve(self, uuid):
        return self._driver.retrieve(self, uuid)

    def delete(self, uuid):
        return self._driver.delete(self, uuid)

    def list(self):
        return self._driver.list(self)


class _NamedStore(_BaseStore):

    def create(self, name, contents):
        return self._driver.create(self, name, contents)

    def update(self, uuid, name, contents):
        return self._driver.update(self, uuid, name, contents)

    def retrieve_by_name(self, name):
        return self._driver.retrieve_by_name(self, name)


class _VersionedStore(_NamedStore):

    def retrieve_by_name(self, name, version=None):
        return self._driver.retrieve_by_name(self, name, version)

    def list(self, only_latest=False):
        return self._driver.list(self, only_latest=only_latest)


class TemplateStore(_VersionedStore):
    object_type = "template"


class EnvironmentFileStore(_BaseStore):
    object_type = "environment"


class RoleStore(_VersionedStore):
    object_type = "role"


class DeploymentPlanStore(_NamedStore):
    object_type = "deployment_plan"
