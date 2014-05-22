#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sqlalchemy import (Column, ForeignKey, Integer, MetaData, Table)


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)

    overclouds = Table('overclouds', meta, autoload=True)
    Table('user_creds', meta, autoload=True)
    user_creds_id = Column('user_creds_id', Integer,
                           ForeignKey('user_creds.id'),
                           nullable=True)

    user_creds_id.create(overclouds)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    overclouds = Table('overclouds', meta, autoload=True)
    overclouds.c.user_creds_id.drop()
