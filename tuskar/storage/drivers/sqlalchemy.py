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

from tuskar.db.sqlalchemy.models import StoredFile
from tuskar.openstack.common.db.sqlalchemy import session as db_session
from tuskar.storage.drivers.base import BaseDriver
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

    def create(self, store, name, contents):

        object_type = store.object_type

        session = get_session()
        session.begin()

        stored_file = StoredFile(
            uuid=str(uuid4()),
            contents=contents,
            object_type=object_type,
            name=name,
        )

        try:
            session.add(stored_file)
            session.commit()
            file_dict = stored_file.as_dict()
            file_dict.pop('object_type')
            file_dict['store'] = store
            return StorageModel(**file_dict)
        finally:
            session.close()

    def retrieve(self, store, uuid):

        object_type = store.object_type

        session = get_session()

        try:
            stored_file = session.query(StoredFile).filter_by(
                uuid=uuid,
                object_type=object_type,
            ).one()
        finally:
            session.close()

        return stored_file

    def update(self, store, uuid, name, contents):

        object_type = store.object_type

        session = get_session()
        session.begin()

        stored_file = StoredFile(
            uuid=uuid,
            contents=contents,
            object_type=object_type,
            name=name,
        )

        try:
            session.add(stored_file)
            session.commit()
        finally:
            session.close()

    def delete(self, store, uuid):

        session = get_session()
        session.begin()

        stored_file = self.retrieve(store, uuid)

        try:
            session.delete(stored_file)
            session.commit()
        finally:
            session.close()

    def list(self, store, only_latest=False):

        object_type = store.object_type

        session = get_session()
        roles = session.query(StoredFile).filter_by(object_type=object_type)
        session.close()
        return roles

    def retrieve_by_name(self, store, name, version=None):

        object_type = store.object_type

        session = get_session()

        try:
            query = session.query(StoredFile).filter_by(
                name=name,
                object_type=object_type,
            )
            if version is not None:
                query = query.filter_by(version=version)

            stored_file = query.one()
        finally:
            session.close()

        return stored_file
