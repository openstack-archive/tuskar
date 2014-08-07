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
TABLE_OVERCLOUD_ROLE = 'overcloud_roles'
TABLE_OVERCLOUD_ROLE_COUNT = 'overcloud_role_counts'


class TuskarBase(models.TimestampMixin, models.ModelBase):
    """Base class for all Tuskar domain models."""
    metadata = None

    def as_dict(self):
        d = dict([(c.name, self[c.name]) for c in self.__table__.columns])
        return d


Base = declarative_base(cls=TuskarBase)


class OvercloudRole(Base):
    """Overcloud role domain model.

    Represents a type of entity that is deployed into the undercloud to create
    the overcloud. For example, a controller or a compute node.
    """

    __tablename__ = TABLE_OVERCLOUD_ROLE

    # Unique identifier for the role
    id = Column(Integer, primary_key=True)

    # User-readable display name of the role
    name = Column(String(length=LENGTH_NAME), nullable=False, unique=True)

    # User-readable text describing what the role does
    description = Column(String(length=LENGTH_DESCRIPTION))

    # Name of the image, in Glance, that is used when creating an instance of
    # this role.
    # Note: This should be the image UUID, but due to Icehouse time constraints
    #       the user will create the image on their own with a pre-defined
    #       name and the image referenced through that.
    # Note: In the future, we will likely support multiple images for a
    #       role, so this will likely change to its own table and a FK
    #       relationship. jdob, Jan 10, 2014
    image_name = Column(String(length=64))

    # UUID of the flavor of node this role should be deployed on.
    # Example: f03266e8-5c99-471c-9eac-375772b45a43
    # Note: In the future, we will likely support multiple flavors for
    #       a role, so this will likely change. jdob, Feb 5, 2014
    flavor_id = Column(String(length=36))

    def __eq__(self, other):
        return self.name == other.name


class OvercloudRoleCount(Base):
    """Configuration for an overcloud role's deployment in an overcloud.

    Maps an overcloud role definition to number of instances to be
    deployed into an overcloud.

    Note: In the future this will likely be enhanced to include the
    flavor of node being deployed on.
    """

    __tablename__ = TABLE_OVERCLOUD_ROLE_COUNT

    # Unique identifier for the deployment configuration
    id = Column(Integer, primary_key=True)

    # Role being configured
    overcloud_role_id = Column(
        Integer,
        ForeignKey('%s.id' % TABLE_OVERCLOUD_ROLE),
        nullable=False
    )

    # Overcloud in which the role is being deployed
    overcloud_id = Column(
        Integer,
        ForeignKey('%s.id' % TABLE_OVERCLOUD, ondelete='CASCADE'),
        nullable=False
    )

    # Number of nodes of this configuration that should be deployed
    num_nodes = Column(Integer, nullable=False)

    # Reference to the full role (this is not the foreign key relationship,
    # that's overcloud_role_id above, this is to eager load the role data).
    overcloud_role = relationship(OvercloudRole.__name__)

    def __eq__(self, other):
        return (self.overcloud_role_id == other.overcloud_role_id
                and self.overcloud_id == other.overcloud_id)


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
                          ForeignKey('%s.id' % TABLE_OVERCLOUD,
                                     ondelete='CASCADE'),
                          nullable=False)

    # Identifier and value of the configuration attribute
    key = Column(String(length=64), nullable=False)
    value = Column(Text())

    def __eq__(self, other):
        return (self.overcloud_id == other.overcloud_id
                and self.key == other.key)


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
    attributes = relationship(OvercloudAttribute.__name__,
                              cascade='all,delete')

    # List of counts of overcloud roles to deploy
    counts = relationship(OvercloudRoleCount.__name__,
                          cascade='all,delete')

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


class StoredFile(Base):
    """Tuskar Stored File

    The StoredFile model is used by the tuskar.storage package and more
    specifically for the SQLAlchemy storage driver. Simply put it is a
    collection of text files with some metadata.
    """

    __tablename__ = "stored_file"

    #: UUID's are used as the unique identifier.
    uuid = Column(String(length=36), primary_key=True)

    #: contents contains the full file contents as a string.
    contents = Column(String(), nullable=False)

    #: Object type flags the type of file that this is, i.e. template or
    #: environment file.
    object_type = Column(String(length=20), nullable=False)

    #: Names provide a short human readable description of a file.
    name = Column(String(length=64), nullable=True)

    #: Versions are an automatic incrementing count.
    version = Column(Integer(), nullable=True)
