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

from tuskar.openstack.common import jsonutils
from tuskar.storage import get_driver


class _BaseStore(object):
    """Base class for all stores.

    This defines the basic CRUD operations and how they will be called to the
    underlying driver.
    """

    #: Object type is used to help the driver know how to store an object. For
    #: example a database may use different tables for objects and a service
    #: like swift may use different containers.
    object_type = None

    def __init__(self, driver=None):
        """Given the driver to be used, set up an instance of the store.

        :param driver: The type of object, used for routing the storage.
        :type  driver: tuskar.storage.drivers.base.BaseDriver
        """
        self._driver = driver or get_driver(self.__class__)

    def create(self, contents):
        """Given the contents create a new file in this store and return a
        `StoredFile` instance representing it.

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """

        return self._driver.create(self, None, contents)

    def retrieve(self, uuid):
        """Returns the file in this store that matches the provided UUID.

        :param uuid: UUID of the object to retrieve.
        :type  uuid: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """
        return self._driver.retrieve(self, uuid)

    def update(self, uuid, contents):
        """Given the uuid and contents update the existing stored file
        and return an instance of StoredFile that reflects the updates.

        :param uuid: UUID of the object to update.
        :type  uuid: str

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """
        return self._driver.update(self, uuid, None, contents)

    def delete(self, uuid):
        """Delete the file in this store with the matching uuid.

        :param uuid: UUID of the object to update.
        :type  uuid: str
        """
        return self._driver.delete(self, uuid)

    def list(self):
        """Return a list of all the stored objects in this store.

        :return: List of StoredFile instances
        :rtype:  [tuskar.storage.models.StoredFile]
        """
        return self._driver.list(self)


class _NamedStore(_BaseStore):
    """The Named Store adds the requirement of a name attribute.

    This extends the base CRUD operations to add the requirement of a name
    where required.
    """

    def create(self, name, contents):
        """Given the name and contents create a new file and return a
        `StoredFile` instance representing it.

        When working with files that are not named, such as an EnvironmentFile
        name must be explicitly passed as None.

        :param name: name of the object to store (optional)
        :type  name: str or None

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """
        return self._driver.create(self, name, contents)

    def update(self, uuid, name, contents):
        """Given the uuid, name and contents update the existing stored file
        and return an instance of StoredFile that reflects the updates.

        :param uuid: UUID of the object to update.
        :type  uuid: str

        :param name: name of the object to store (optional)
        :type  name: str

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """
        return self._driver.update(self, uuid, name, contents)

    def retrieve_by_name(self, name):
        """Returns the stored file for a given store that matches the provided
        name.

        :param name: name of the object to retrieve.
        :type  name: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """
        return self._driver.retrieve_by_name(self, name)


class _VersionedStore(_NamedStore):

    def retrieve_by_name(self, name, version=None):
        """Returns the stored file for a given store that matches the provided
        name and optionally version. If the version isn't provided, the latest
        is returned.

        :param name: name of the object to retrieve.
        :type  name: str

        :param version: Version of the object to retrieve. If the version isn't
                        provided, the latest will be returned.
        :type  version: int

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """
        return self._driver.retrieve_by_name(self, name, version)

    def list(self, only_latest=False):
        """Return a list of all the stored objects in this store.

        :param only_latest: If set to True only the latest versions of each
                            object will be returned.
        :type  only_latest: bool

        :return: List of StoredFile instances
        :rtype:  [tuskar.storage.models.StoredFile]
        """
        return self._driver.list(self, only_latest=only_latest)


class TemplateStore(_VersionedStore):
    """Template Store for Heat Orchestration TemplateStore

    Templates are named and versioned.
    """
    object_type = "template"


class EnvironmentFileStore(_BaseStore):
    """Environment File for Heat environment files.

    Environment Files are not named and don't contain versions.
    """
    object_type = "environment"


class RoleStore(_VersionedStore):
    """Role Store

    Roles are named and versioned.
    """
    object_type = "role"


class DeploymentPlanStore(_NamedStore):
    """Deployment Plan Store

    Deployment plans are named but not versioned.
    """
    object_type = "deployment_plan"

    def __init__(self, *args, **kwargs):
        super(DeploymentPlanStore, self).__init__(*args, **kwargs)

        self.template_store = TemplateStore()
        self.env_file_store = EnvironmentFileStore()

    def _serialise(self, master_template, environment_file):
        """Given the master_template and environment_file UUID's create a
        simple dictionary representation of the Plan and serialise it to JSON.

        :param master_template: Master template UUID
        :type  master_template: str

        :param environment_file: Environment File UUID.
        :type  environment_file: str

        :return: JSON String
        :rtype:  str
        """

        plan = {
            "master_teplate_uuid": master_template,
            "environment_file_uuid": environment_file
        }

        return jsonutils.dumps(plan)

    def _deserialise(self, content):
        """Load the Plan from a JSON string containing the master template
        UUID and the environment file UUID.

        :param content: JSON String
        :type  content: str

        :return: 2-tuple of Template and Environment StoredFile instances
        :rtype: tulpe(tuskar.storage.models.StoredFile, )
        """

        plan = jsonutils.loads(content)

        master = self.template_store.retrieve(plan['master_template_uuid'])
        env = self.env_file_store.retrieve(plan['environment_file_uuid'])

        return master, env

    def _create_empty_master_template(self, name):
        empty_file = ""
        master_template = self.template_store.create(name, empty_file)
        return master_template

    def _create_empty_environment_file(self):
        empty_file = ""
        environment_file = self.env_file_store.create(empty_file)
        return environment_file

    def create(self, name, master_template_uuid=None, environment_uuid=None):

        if master_template_uuid is None:
            master_template = self._create_empty_master_template(name)
            master_template_uuid = master_template.uuid

        if environment_uuid is None:
            environment = self._create_empty_environment_file()
            environment_uuid = environment.uuid

        contents = self._serialise(master_template_uuid, environment_uuid)
        super(DeploymentPlanStore, self).create(name, contents)

    def retrieve(self, uuid):

        stored_file = self._driver.retrieve(self, uuid)
        contents = stored_file.contents
        master_template, environment_file = self.deserialise(contents)
        return master_template, environment_file

    def update(self, uuid, name, master_template_uuid=None,
               environment_uuid=None):

        if master_template_uuid is None:
            master_template = self._create_empty_master_template(name)
            master_template_uuid = master_template.uuid

        if environment_uuid is None:
            environment = self._create_empty_environment_file()
            environment_uuid = environment.uuid

        contents = self._serialise(master_template_uuid, environment_uuid)
        super(DeploymentPlanStore, self).update(uuid, name, contents)

    def delete(self, uuid):
        return self._driver.delete(self, uuid)

    def list(self):
        return self._driver.list(self)
