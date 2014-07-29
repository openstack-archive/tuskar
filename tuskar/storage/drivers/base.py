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

    @abstractmethod
    def create(self, store, name, contents):
        """Given the store, name and contents create a new file and return a
        `StoredFile` instance representing it.

        When working file files that are not named, such as an EnvironmentFile
        name must be explicitly passed as None.

        :param store: The type of object, used for routing the storage.
        :type  store: str

        :param name: name of the object to store (optional)
        :type  name: str or None

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoreFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """

    @abstractmethod
    def retrieve(self, store, uuid):
        """Returns the stored file for a given store that matches the provided
        UUID.

        :param store: The type of object, used for routing the storage.
        :type  store: str

        :param uuid: UUID of the object to retrieve.
        :type  uuid: str

        :return: StoreFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """

    @abstractmethod
    def update(self, store, uuid, name, contents):
        """Given the store, name and contents update the existing stored file
        and return an instance of StoredFile that reflects the updates.

        :param store: The type of object, used for routing the storage.
        :type  store: str

        :param uuid: UUID of the object to update.
        :type  uuid: str

        :param name: name of the object to store (optional)
        :type  name: str

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoreFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """

    @abstractmethod
    def delete(self, store, uuid):
        """Delete the stored file with the UUID under the given store.

        :param store: The type of object, used for routing the storage.
        :type  store: str

        :param uuid: UUID of the object to update.
        :type  uuid: str
        """

    @abstractmethod
    def list(self, store):
        """Return a list of all the stored objects for a given store.

        :param store: The type of object, used for routing the storage.
        :type  store: str

        :return: List of StoreFile instances
        :rtype:  [tuskar.storage.models.StoredFile]
        """

    @abstractmethod
    def retrieve_by_name(self, store, name, version=None):
        """Returns the stored file for a given store that matches the provided
        UUID and optionally version.

        :param store: The type of object, used for routing the storage.
        :type  store: str

        :param name: name of the object to retrieve.
        :type  name: str

        :param version: Version of the object to retrieve. If the version isn't
                        provided, the latest will be returned.
        :type  version: int

        :return: StoreFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """
