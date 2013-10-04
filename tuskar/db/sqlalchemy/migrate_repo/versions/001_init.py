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
from sqlalchemy import DateTime, Integer, String

from tuskar.openstack.common import log as logging

LOG = logging.getLogger(__name__)

ENGINE = 'InnoDB'
CHARSET = 'utf8'


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    capacities = Table('capacities', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('name', String(length=64)),
        Column('value', String(length=128)),
        Column('unit', String(length=24)),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    racks = Table('racks', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('name', String(length=128)),
        Column('slots', Integer, default=0),
        Column('state', String(length=128), default='unprovisioned'),
        Column('subnet', String(length=128)),
        Column('location', String(length=128)),
        Column('resource_class_id', Integer,
               ForeignKey('resource_classes.id')),
        Column('chassis_id', String(length=64)),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    nodes = Table('nodes', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('node_id', String(length=64)),
        Column('rack_id', Integer, ForeignKey('racks.id')),
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

    flavor_capacities = Table('flavor_capacities', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('capacity_id', Integer, ForeignKey('capacities.id')),
        Column('flavor_id', Integer, ForeignKey('flavors.id')),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    resource_classes = Table('resource_classes', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('name', String(length=128)),
        Column('service_type', String(length=128)),
        Column('image_id', String(length=36)),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    flavors = Table('flavors', meta,
        #FIXME - id should be UUID string
        Column('id', Integer, primary_key=True, nullable=False),
        Column('name', String(length=128)),
        Column('resource_class_id', Integer,
               ForeignKey('resource_classes.id')),
        Column('nova_flavor_uuid', String(36)),
        Column('max_vms', Integer),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        mysql_engine=ENGINE,
        mysql_charset=CHARSET,
    )

    tables = [resource_classes, capacities, racks, nodes, flavors,
              rack_capacities, flavor_capacities]

    for table in tables:
        try:
            table.create()
        except Exception:
            LOG.info(repr(table))
            LOG.exception(_('Exception while creating table.'))
            raise

    indexes = [
    ]

    uniques = [
        UniqueConstraint('name', table=resource_classes,
                         name='uniq_resource_classes0name'),
        UniqueConstraint('name', table=racks,
                         name='racks_name_ux'),

        # The 'node_id' in nodes table must be unique
        # so Tuskar Node <-> Ironic Node mapping is 1:1
        #
        UniqueConstraint('node_id', table=nodes,
                         name='node_node_id_ux'),
    ]

    for index in indexes:
        index.create(migrate_engine)
    for index in uniques:
        index.create(migrate_engine)


def downgrade(migrate_engine):
    raise NotImplementedError('Downgrade is unsupported.')
