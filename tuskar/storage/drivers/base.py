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
from abc import abstractmethod

from six import add_metaclass


@add_metaclass(ABCMeta)
class BaseDriver(object):
    """Base Storage Drivers

    The BaseDriver provides the abstract interface for storage drivers. It is
    intended that a driver will be used by multiple stores (which are defined)
    in tuskar.storages.stores).

    Each method is passed an instance of the store that is using it, this
    allows the driver to direct operations. For example, a database backend
    may use different tables for different stores (templates and environments)
    or a swift backend implementation could use different containers.
    """

    @abstractmethod
    def create(self, store, name, contents):
        """Given the store, name and contents create a new file and return a
        `StoredFile` instance representing it.

        Some of the stored items such as environment files do not have names.
        When working with these, name must be passed explicitly as None. This
        is why the name has a type of "str or None" below.

        :param store: The store class, used for routing the storage.
        :type  store: tuskar.storage.stores._BaseStore

        :param name: name of the object to store (optional)
        :type  name: str or None

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile

        :raises: tuskar.storage.exceptions.NameAlreadyUsed if the name is
            already in use
        """

    @abstractmethod
    def retrieve(self, store, uuid):
        """Returns the stored file for a given store that matches the provided
        UUID.

        :param store: The store class, used for routing the storage.
        :type  store: tuskar.storage.stores._BaseStore

        :param uuid: UUID of the object to retrieve.
        :type  uuid: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
            found
        """

    @abstractmethod
    def update(self, store, uuid, contents):
        """Given the store, uuid, name and contents update the existing stored
        file and return an instance of StoredFile that reflects the updates.
        Either name and/or contents can be provided. If they are not then they
        will remain unchanged.

        :param store: The store class, used for routing the storage.
        :type  store: tuskar.storage.stores._BaseStore

        :param uuid: UUID of the object to update.
        :type  uuid: str

        :param contents: String containing the file contents (optional)
        :type  contents: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
            found
        """

    @abstractmethod
    def delete(self, store, uuid):
        """Delete the stored file with the UUID under the given store.

        :param store: The store class, used for routing the storage.
        :type  store: tuskar.storage.stores._BaseStore

        :param uuid: UUID of the object to delete.
        :type  uuid: str

        :return: Returns nothing on success. Exceptions are expected for errors
        :rtype: None

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
                 found
        """

    @abstractmethod
    def list(self, store, only_latest=False):
        """Return a list of all the stored objects for a given store.
        Optionally only_latest can be set to True to return only the most
        recent version of each objects (grouped by name).

        :param store: The store class, used for routing the storage.
        :type  store: tuskar.storage.stores._BaseStore

        :param only_latest: If set to True only the latest versions of each
                            object will be returned.
        :type  only_latest: bool

        :return: List of StoredFile instances
        :rtype:  [tuskar.storage.models.StoredFile]
        """

    @abstractmethod
    def retrieve_by_name(self, store, name, version=None):
        """Returns the stored file for a given store that matches the provided
        name and optionally version.

        :param store: The store class, used for routing the storage.
        :type  store: tuskar.storage.stores._BaseStore

        :param name: name of the object to retrieve.
        :type  name: str

        :param version: Version of the object to retrieve. If the version isn't
                        provided, the latest will be returned.
        :type  version: int

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile

        :raises: tuskar.storage.exceptions.UnknownName if the name can't be
                 found
        :raises: tuskar.storage.exceptions.UnknownVersion if the version can't
                 be found
        """
