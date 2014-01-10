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

"""
Tuskar domain models for use with SQLAlchemy.
"""

from oslo.config import cfg

from sqlalchemy import (Column, ForeignKey, Integer, String, Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from tuskar.openstack.common.db.sqlalchemy import models


sql_opts = [
    cfg.StrOpt('mysql_engine',
               default='InnoDB',
               help='MySQL engine')
]

cfg.CONF.register_opts(sql_opts)


# Column lengths for common attributes
LENGTH_NAME = 64
LENGTH_DESCRIPTION = 256
LENGTH_HOST = 32
LENGTH_USERNAME = 64
LENGTH_PASSWORD = 64


class TuskarBase(models.TimestampMixin, models.ModelBase):
    """Base class for all Tuskar domain models."""
    metadata = None

Base = declarative_base(cls=TuskarBase)


class ResourceCategory(Base):
    """Resource category domain model.

    Represents a type of entity that is deployed into the undercloud to create
    the overcloud. For example, a controller or a compute node.
    """

    __tablename__ = 'resource_categories'

    # Unique identifier for the category
    id = Column(Integer, primary_key=True)

    # User-readable display name of the category
    name = Column(String(length=LENGTH_NAME), nullable=False, unique=True)

    # User-readable text describing what the category does
    description = Column(String(length=LENGTH_DESCRIPTION))

    # UUID of the image, in Glance, that is used when creating an instance of
    # this category
    # Note: In the future we will likely support multiple images for a
    #       category, so this will likely change to its own table and a FK
    #       relationship. jdob, Jan 10, 2014
    image_id = Column(String(length=36))


class NodeProfile(Base):
    """Node profile domain model.

    Describes the characteristics of a node on which a particular resource
    category can be deployed. Each resource category will have one or more
    profiles associated with it.

    *** For Icehouse, this model is currently not used. The current state
        reflects the initial discussions from the wireframes but more
        design is needed.
    """

    __tablename__ = 'node_profiles'

    # Unique identifier for the profile
    id = Column(Integer, primary_key=True)

    # Foreign key linking a profile back into its category
    category_id = Column(Integer,
                         ForeignKey('%s.id' % ResourceCategory.__tablename__))

    # Minimum CPU cores the node should have
    min_cpu = Column(Integer)

    # Minimum memory, in GB, the node should have
    min_memory = Column(Integer)

    # Minimum disk size, in TB, the node should have
    min_local_disk = Column(Integer)

    # Comma-separated list of tags to be assigned to the node
    tags = Column(String(length=512))


class OvercloudAttribute(Base):
    """Overcloud-level configuration attribute domain model.

    Contains a single configuration parameter for an overcloud. These
    attributes include configuration for the overcloud database,
    message bus, and keystone instance.
    """

    __tablename__ = 'overcloud_attributes'

    # Unique identifier for the overcloud
    id = Column(Integer, primary_key=True)

    # Reference back to the overcloud being configured
    overcloud_id = Column(Integer, ForeignKey('overclouds.id'),
                          nullable=False)

    # Identifier and value of the configuration attribute
    key = Column(String(length=64), nullable=False)
    value = Column(Text())


class Overcloud(Base):
    """Overcloud domain model.

    Represents the configuration of a cloud deployed into the undercloud by
    Tuskar.
    """

    __tablename__ = 'overclouds'

    # Unique identifier for the overcloud
    id = Column(Integer, primary_key=True)

    # User-readable name of the overcloud
    name = Column(String(length=LENGTH_NAME), nullable=False, unique=True)

    # User-readable text describing the overcloud
    description = Column(String(length=LENGTH_DESCRIPTION))

    # List of configuration attributes for the overcloud
    attributes = relationship(OvercloudAttribute.__name__)
