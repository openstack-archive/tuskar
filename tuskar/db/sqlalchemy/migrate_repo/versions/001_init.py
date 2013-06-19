# vim: tabstop=4 shiftwidth=4 softtabstop=4
# -*- encoding: utf-8 -*-
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
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


from migrate.changeset import UniqueConstraint
from sqlalchemy import Table, Column, ForeignKey, MetaData
from sqlalchemy import DateTime, Integer, String, Text

from tuskar.openstack.common import log as logging

LOG = logging.getLogger(__name__)

ENGINE = 'InnoDB'
CHARSET = 'utf8'


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    blaas = Table('blaas', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('uuid', String(length=36)),
        Column('description', Text),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    sausages = Table('sausages', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('name', Text),
        Column('blaa_id', Integer, ForeignKey('blaas.id'),
            nullable=True),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    capacities = Table('capacities', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('name', String(length=64)),
        Column('value', String(length=128)),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    racks = Table('racks', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('name', String(length=128)),
        Column('slots', Integer),
        Column('subnet', String(length=128)),
        Column('chassis_url', Text),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    rack_capacities = Table('rack_capacities', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('capacity_id', Integer, ForeignKey('capacities.id')),
        Column('rack_id', Integer, ForeignKey('racks.id')),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    tables = [blaas, sausages, capacities, racks, rack_capacities]

    for table in tables:
        try:
            table.create()
        except Exception:
            LOG.info(repr(table))
            LOG.Exception(_('Exception while creating table.'))
            raise

    indexes = [
    ]

    uniques = [
        UniqueConstraint('uuid', table=blaas,
                         name='blaas_uuid_ux'),
        UniqueConstraint('name', table=sausages,
                         name='sausages_name_ux'),
    ]

    if migrate_engine.name == 'mysql' or migrate_engine.name == 'postgresql':
        for index in indexes:
            index.create(migrate_engine)
        for index in uniques:
            index.create(migrate_engine)


def downgrade(migrate_engine):
    raise NotImplementedError('Downgrade is unsupported.')
