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

TABLE_NODE_PROFILE = 'node_profiles'
TABLE_OVERCLOUD = 'overclouds'
TABLE_OVERCLOUD_ATTRIBUTES = 'overcloud_attributes'
TABLE_RESOURCE_CATEGORY = 'resource_categories'
TABLE_OVERCLOUD_CATEGORY_COUNT = 'overcloud_category_counts'


class TuskarBase(models.TimestampMixin, models.ModelBase):
    """Base class for all Tuskar domain models."""
    metadata = None

    def as_dict(self):
        d = dict([(c.name, self[c.name]) for c in self.__table__.columns])
        return d


Base = declarative_base(cls=TuskarBase)


class ResourceCategory(Base):
    """Resource category domain model.

    Represents a type of entity that is deployed into the undercloud to create
    the overcloud. For example, a controller or a compute node.
    """

    __tablename__ = TABLE_RESOURCE_CATEGORY

    # Unique identifier for the category
    id = Column(Integer, primary_key=True)

    # User-readable display name of the category
    name = Column(String(length=LENGTH_NAME), nullable=False, unique=True)

    # User-readable text describing what the category does
    description = Column(String(length=LENGTH_DESCRIPTION))

    # Name of the image, in Glance, that is used when creating an instance of
    # this category.
    # Note: This should be the image UUID, but due to Icehouse time constraints
    #       the user will create the image on their own with a pre-defined
    #       name and the image referenced through that.
    # Note: In the future, we will likely support multiple images for a
    #       category, so this will likely change to its own table and a FK
    #       relationship. jdob, Jan 10, 2014
    image_name = Column(String(length=64))

    # UUID of the flavor of node this role should be deployed on.
    # Example: f03266e8-5c99-471c-9eac-375772b45a43
    # Note: In the future, we will likely support multiple flavors for
    #       a role, so this will likely change. jdob, Feb 5, 2014
    flavor_id = Column(String(length=36))

    def __eq__(self, other):
        return self.name == other.name


class OvercloudCategoryCount(Base):
    """Configuration for a resource category's deployment in an overcloud.

    Maps a resource category definition to number of instances, of a
    particular node profile, to be deployed into an overcloud.
    """

    __tablename__ = TABLE_OVERCLOUD_CATEGORY_COUNT

    # Unique identifier for the deployment configuration
    id = Column(Integer, primary_key=True)

    # Resource category being configured
    resource_category_id = \
        Column(Integer,
               ForeignKey('%s.id' % TABLE_RESOURCE_CATEGORY),
               nullable=False)

    # Overcloud in which the resource category is being deployed
    overcloud_id = \
        Column(Integer,
               ForeignKey('%s.id' % TABLE_OVERCLOUD),
               nullable=False)

    # Currently commented out until we finish deciding on how these will
    # be handled for Icehouse.
    # node_profile_id

    # Number of nodes of this configuration that should be deployed
    num_nodes = Column(Integer, nullable=False)

    def __eq__(self, other):
        return self.resource_category_id == other.resource_category_id \
               and self.overcloud_id == other.overcloud_id


class OvercloudAttribute(Base):
    """Overcloud-level configuration attribute domain model.

    Contains a single configuration parameter for an overcloud. These
    attributes include configuration for the overcloud database,
    message bus, and keystone instance.
    """

    __tablename__ = TABLE_OVERCLOUD_ATTRIBUTES

    # Unique identifier for the overcloud
    id = Column(Integer, primary_key=True)

    # Reference back to the overcloud being configured
    overcloud_id = Column(Integer,
                          ForeignKey('%s.id' % TABLE_OVERCLOUD),
                          nullable=False)

    # Identifier and value of the configuration attribute
    key = Column(String(length=64), nullable=False)
    value = Column(Text())

    def __eq__(self, other):
        return self.overcloud_id == other.overcloud_id \
               and self.key == other.key


class Overcloud(Base):
    """Overcloud domain model.

    Represents the configuration of a cloud deployed into the undercloud by
    Tuskar.
    """

    __tablename__ = TABLE_OVERCLOUD

    # Unique identifier for the overcloud
    id = Column(Integer, primary_key=True)

    # UUID of the stack, in Heat, that was created from this configuration
    stack_id = Column(String(length=36))

    # User-readable name of the overcloud
    name = Column(String(length=LENGTH_NAME), nullable=False, unique=True)

    # User-readable text describing the overcloud
    description = Column(String(length=LENGTH_DESCRIPTION))

    # List of configuration attributes for the overcloud
    attributes = relationship(OvercloudAttribute.__name__)

    # List of counts of resource categories to deploy
    counts = relationship(OvercloudCategoryCount.__name__)

    def __eq__(self, other):
        return self.name == other.name

    def as_dict(self):
        d = dict([(c.name, self[c.name]) for c in self.__table__.columns])

        # Foreign keys aren't picked up by the base as_dict, so add them in
        # here
        attribute_dicts = [a.as_dict() for a in self.attributes]
        d['attributes'] = attribute_dicts

        count_dicts = [c.as_dict() for c in self.counts]
        d['counts'] = count_dicts

        return d
