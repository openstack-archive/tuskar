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

from __future__ import absolute_import

from uuid import uuid4

from oslo.config import cfg
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from tuskar.db.sqlalchemy.models import StoredFile
from tuskar.openstack.common.db.sqlalchemy import session as db_session
from tuskar.storage.drivers.base import BaseDriver
from tuskar.storage.exceptions import NameAlreadyUsed
from tuskar.storage.exceptions import UnknownName
from tuskar.storage.exceptions import UnknownUUID
from tuskar.storage.exceptions import UnknownVersion
from tuskar.storage.models import StoredFile as StorageModel

sql_opts = [
    cfg.StrOpt('mysql_engine',
               default='InnoDB',
               help='MySQL engine')
]

cfg.CONF.register_opts(sql_opts)


def get_session():
    return db_session.get_session(sqlite_fk=True)


class SQLAlchemyDriver(BaseDriver):

    def _generate_uuid(self):
        return str(uuid4())

    def _to_storage_model(self, store, result):
        """Convert a result from SQLAlchemy into an instance of the common
        model used in the tuskar.storage.

        :param store: Instance of the storage store
        :type  store: tuskat.storage.stores._BaseStore

        :param result: Instance of the SQLAlchemy model as returned by a query.
        :type  result: tuskar.db.sqlalchemy.models.StoredFile

        :return: Instance of the StoredFile class.
        :rtype: tuskar.storage.models.StoredFile
        """
        file_dict = result.as_dict()
        file_dict.pop('object_type')
        file_dict['store'] = store
        return StorageModel(**file_dict)

    def _upsert(self, store, stored_file):

        session = get_session()
        session.begin()

        try:
            session.add(stored_file)
            session.commit()
            return self._to_storage_model(store, stored_file)
        finally:
            session.close()

    def _get_latest_version(self, store, name):

        session = get_session()

        try:
            return session.query(
                func.max(StoredFile.version)
            ).filter_by(
                object_type=store.object_type, name=name
            ).scalar()
        finally:
            session.close()

    def _create(self, store, name, contents, version):

        stored_file = StoredFile(
            uuid=self._generate_uuid(),
            contents=contents,
            object_type=store.object_type,
            name=name,
            version=version
        )

        return self._upsert(store, stored_file)

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
        """

        if store.versioned:
            version = 1
        else:
            version = None

        if name is not None:
            try:
                self.retrieve_by_name(store, name)
                msg = "A file with the name '{0}' already exists".format(name)
                raise NameAlreadyUsed(msg)
            except UnknownName:
                pass

        return self._create(store, name, contents, version)

    def _retrieve(self, object_type, uuid):

        session = get_session()
        try:
            return session.query(StoredFile).filter_by(
                uuid=uuid,
                object_type=object_type
            ).one()
        except NoResultFound:
            msg = "No results found for the UUID: {0}".format(uuid)
            raise UnknownUUID(msg)
        finally:
            session.close()

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

        stored_file = self._retrieve(store.object_type, uuid)
        return self._to_storage_model(store, stored_file)

    def update(self, store, uuid, contents):
        """Given the store, uuid, name and contents update the existing stored
        file and return an instance of StoredFile that reflects the updates.
        Either name and/or contents can be provided. If they are not then they
        will remain unchanged.

        :param store: The store class, used for routing the storage.
        :type  store: tuskar.storage.stores._BaseStore

        :param uuid: UUID of the object to update.
        :type  uuid: str

        :param name: name of the object to store (optional)
        :type  name: str

        :param contents: String containing the file contents (optional)
        :type  contents: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
                 found
        """

        stored_file = self._retrieve(store.object_type, uuid)

        stored_file.contents = contents

        if store.versioned:
            version = self._get_latest_version(store, stored_file.name) + 1
            return self._create(
                store, stored_file.name, stored_file.contents, version)

        return self._upsert(store, stored_file)

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

        session = get_session()
        session.begin()

        stored_file = self._retrieve(store.object_type, uuid)

        try:
            session.delete(stored_file)
            session.commit()
        finally:
            session.close()

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

        object_type = store.object_type

        session = get_session()
        try:
            files = session.query(StoredFile).filter_by(
                object_type=object_type
            )

            if only_latest:
                # When only_latest is provided, then we want to select only the
                # stored files with the latest version. To do this we use a
                # subquery to get a set of names and latest versions for the
                # object type. After we have that, we join in the name and
                # version to make sure we match it.
                stmt = session.query(
                    StoredFile.name,
                    func.max(StoredFile.version).label("version")
                ).filter_by(
                    object_type=object_type
                ).group_by(
                    StoredFile.name
                ).subquery()

                # join our existing query on the subquery.
                files = files.join(
                    stmt,
                    and_(
                        StoredFile.name == stmt.c.name,
                        StoredFile.version == stmt.c.version,
                    )
                )

            return [self._to_storage_model(store, file_) for file_ in files]
        finally:
            session.close()

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

        object_type = store.object_type

        session = get_session()

        try:
            query = session.query(StoredFile).filter_by(
                name=name,
                object_type=object_type,
            )
            if version is not None:
                query = query.filter_by(version=version)
            else:
                query = query.filter_by(
                    version=self._get_latest_version(store, name)
                )

            stored_file = query.one()
            return self._to_storage_model(store, stored_file)
        except NoResultFound:

            name_query = session.query(StoredFile).filter_by(
                name=name,
                object_type=object_type,
            )

            if name_query.count() == 0:
                msg = "No results found for the Name: {0}".format(name)
                raise UnknownName(msg)
            elif name_query.filter_by(version=version).count() == 0:
                msg = "No results found for the Version: {0}".format(version)
                raise UnknownVersion(msg)

            raise

        finally:
            session.close()
