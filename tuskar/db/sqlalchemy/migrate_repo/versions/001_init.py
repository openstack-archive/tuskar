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

from migrate.changeset import UniqueConstraint
from sqlalchemy import (Column, DateTime, ForeignKey, Integer,
                        MetaData, String, Table, Text)

from tuskar.db.sqlalchemy import models
from tuskar.openstack.common.gettextutils import _  # noqa
from tuskar.openstack.common import log as logging


LOG = logging.getLogger(__name__)

ENGINE = 'InnoDB'
CHARSET = 'utf8'


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    overcloud_roles = Table(
        'overcloud_roles',
        meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('name', String(length=models.LENGTH_NAME), unique=True),
        Column('description', String(length=models.LENGTH_DESCRIPTION)),
        Column('image_name', String(length=64)),
        Column('flavor_id', String(length=36)),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    overcloud_role_counts = Table(
        'overcloud_role_counts',
        meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('overcloud_role_id',
               Integer,
               ForeignKey('overcloud_roles.id'),
               nullable=False),
        Column('overcloud_id',
               Integer,
               ForeignKey('overclouds.id'),
               nullable=False),
        Column('num_nodes', Integer, nullable=False),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    overcloud = Table(
        'overclouds',
        meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('name', String(length=models.LENGTH_NAME), unique=True),
        Column('description', String(length=models.LENGTH_DESCRIPTION)),
        Column('stack_id', String(length=36)),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    overcloud_attributes = Table(
        'overcloud_attributes',
        meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('key', String(length=64), nullable=False),
        Column('value', Text()),
        Column('overcloud_id',
               Integer,
               ForeignKey('overclouds.id'),
               nullable=False),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    tables = [overcloud_roles, overcloud_role_counts,
              overcloud, overcloud_attributes]

    for table in tables:
        try:
            LOG.info(repr(table))
            table.create()
        except Exception:
            LOG.info(repr(table))
            LOG.exception(_('Exception while creating table.'))
            raise

    indexes = [
    ]

    # There eventually needs to be a uniqueness constraint for
    # overcloud role counts across overcloud role,
    # overcloud, and profile. I'm skipping it for now until we decide
    # on a plan for the node profiles in Icehouse.
    # jdob, Jan 16, 2014

    uniques = [
        UniqueConstraint('name', table=overcloud_roles,
                         name='uniq_overcloud_roles0name'),
        UniqueConstraint('name', table=overcloud,
                         name='uniq_overcloud0name'),
        UniqueConstraint('overcloud_id', 'key', table=overcloud_attributes,
                         name='uniq_overcloud_attributes0overcloud_name')
    ]

    for index in indexes:
        index.create(migrate_engine)

    for index in uniques:
        index.create(migrate_engine)


def downgrade(migrate_engine):
    raise NotImplementedError('Downgrade is unsupported.')
