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


from sqlalchemy import (Column, DateTime, Integer,
                        MetaData, String, Table, Text)

from tuskar.openstack.common import log as logging

LOG = logging.getLogger(__name__)

ENGINE = 'InnoDB'
CHARSET = 'utf8'


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    user_creds = Table(
        'user_creds', meta,
        Column('id', Integer,
               primary_key=True, nullable=False),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('username', String(255)),
        Column('password', String(255)),
        Column('tenant', String(1024)),
        Column('auth_url', Text),
        Column('project_id', String(256)),
        Column('decrypt_method', String(length=64),
               default='tuskar_decrypt'),
        Column('trustor_user_id', String(length=64)),
        Column('trust_id', String(length=255)),

        mysql_engine=ENGINE,
        mysql_charset=CHARSET
    )

    user_creds.create()


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    user_creds = Table('user_creds', meta, autoload=True)
    user_creds.drop()
