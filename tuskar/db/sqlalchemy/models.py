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

"""
SQLAlchemy models.
"""

import json
import logging
import urlparse

from oslo.config import cfg

from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.orm import relationship
from tuskar.openstack.common.db.sqlalchemy import models

sql_opts = [
    cfg.StrOpt('mysql_engine',
               default='InnoDB',
               help='MySQL engine')
]

cfg.CONF.register_opts(sql_opts)


logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def table_args():
    engine_name = urlparse.urlparse(cfg.CONF.database_connection).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': cfg.CONF.mysql_engine,
                'mysql_charset': "utf8"}
    return None


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class TuskarBase(models.TimestampMixin,
                 models.ModelBase):

    metadata = None

    def as_dict(self):
        d = {"id": self['id']}
        for c in self.__table__.columns:
            if c.name == 'id':
                continue
            d[c.name] = self[c.name]
        return d


Base = declarative_base(cls=TuskarBase)


class Capacity(Base):
    """Represents a Capacity."""

    __tablename__ = 'capacities'
    id = Column(Integer, primary_key=True)
    name = Column(String(length=64))
    value = Column(String(length=128))
    unit = Column(String(length=24))


class RackCapacities(Base):
    """Represents a many-to-many relation between Rack and Capacity."""

    __tablename__ = 'rack_capacities'
    id = Column(Integer, primary_key=True)
    rack_id = Column(Integer, ForeignKey('racks.id'), primary_key=True)
    capacity_id = Column(Integer, ForeignKey('capacities.id'),
                         primary_key=True)


class FlavorCapacities(Base):
    """Represents a many-to-many relation between Flavor and Capacity."""
    __tablename__ = 'flavor_capacities'
    id = Column(Integer, primary_key=True)
    #FIXME - I want flavor.id to be UUID String
    flavor_id = Column(Integer, ForeignKey('flavors.id'), primary_key=True)
    capacity_id = Column(Integer, ForeignKey('capacities.id'),
                         primary_key=True)


class Node(Base):
    """Represents a Node."""

    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)
    rack_id = Column(Integer, ForeignKey('racks.id'))
    node_id = Column(String(length=64), unique=True)
    rack = relationship("Rack")


class Rack(Base):
    """Represents a Rack."""

    __tablename__ = 'racks'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    slots = Column(Integer, default=0)
    subnet = Column(String(length=128))
    location = Column(String(length=128))
    state = Column(String(length=128), default='unprovisioned')
    chassis_id = Column(String(length=64))
    resource_class_id = Column(Integer, ForeignKey('resource_classes.id',
                                                   onupdate="cascade"))
    capacities = relationship("Capacity",
                              secondary=
                              Base.metadata.tables['rack_capacities'],
                              cascade="all, delete",
                              lazy='joined')
    nodes = relationship("Node", cascade="all, delete")


class Flavor(Base):
    """Represents a Flavor Class."""

    __tablename__ = 'flavors'
    #FIXME - I want flavor.id to be UUID String
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    resource_class_id = Column(Integer, ForeignKey('resource_classes.id',
                                                   onupdate="cascade"))
    max_vms = Column(Integer)
    nova_flavor_uuid = Column(String(length=128))
    capacities = relationship("Capacity",
            secondary=Base.metadata.tables['flavor_capacities'],
            cascade="all, delete",
            lazy='joined')


class ResourceClass(Base):
    """Represents a Resource Class."""

    __tablename__ = 'resource_classes'
    __table_args__ = (
        UniqueConstraint("name", name="uniq_resource_classes0name"),
    )
    id = Column(Integer, primary_key=True)
    name = Column(String(length=128))
    service_type = Column(Text, unique=True)
    image_id = Column(String(length=36))
    racks = relationship("Rack",
                         backref="resource_class",
                         lazy='joined',
                         cascade="all",
                         passive_updates=False)
    flavors = relationship("Flavor",
                           backref="resource_class",
                           lazy='joined',
                           cascade="all, delete",
                           passive_updates=False)
