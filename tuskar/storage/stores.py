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


class _BaseStore(object):
    """Base class for all stores.

    This defines the basic CRUD operations and how they will be called to the
    underlying driver.
    """

    #: Object type is used to help the driver know how to store an object. For
    #: example a database may use different tables for objects and a service
    #: like swift may use different containers.
    object_type = None

    def __init__(self, driver):
        """Given the driver to be used, set up an instance of the store.

        :param driver: The type of object, used for routing the storage.
        :type  driver: tuskar.storage.drivers.base.BaseDriver
        """
        self._driver = driver

    def create(self, contents):
        """Given the contents create a new file in this store and return a
        `StoredFile` instance representing it.

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoreFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """

        return self._driver.create(self, None, contents)

    def retrieve(self, uuid):
        """Returns the file in this store that matches the provided UUID.

        :param uuid: UUID of the object to retrieve.
        :type  uuid: str

        :return: StoreFile instance containing the file metadata and contents
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

        :return: StoreFile instance containing the file metadata and contents
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

        :return: List of StoreFile instances
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

        When working file files that are not named, such as an EnvironmentFile
        name must be explicitly passed as None.

        :param store: The store class, used for routing the storage.
        :type  store: tuskar.storage.stores._BaseStore

        :param name: name of the object to store (optional)
        :type  name: str or None

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoreFile instance containing the file metadata and contents
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

        :return: StoreFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """
        return self._driver.update(self, uuid, name, contents)

    def retrieve_by_name(self, name):
        """Returns the stored file for a given store that matches the provided
        name.

        :param name: name of the object to retrieve.
        :type  name: str

        :return: StoreFile instance containing the file metadata and contents
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

        :return: StoreFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """
        return self._driver.retrieve_by_name(self, name, version)

    def list(self, only_latest=False):
        """Return a list of all the stored objects in this store.

        :param only_latest: If set to True only the latest versions of each
                            object will be returned.
        :type  only_latest: bool

        :return: List of StoreFile instances
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
