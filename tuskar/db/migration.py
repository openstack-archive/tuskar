# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
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

"""Database setup and migration commands."""

from oslo.config import cfg

from tuskar.common import utils

CONF = cfg.CONF
CONF.import_opt('backend',
                'tuskar.openstack.common.db.api',
                group='database')

IMPL = utils.LazyPluggable(
    pivot='backend',
    config_group='database',
    sqlalchemy='tuskar.db.sqlalchemy.migration')

INIT_VERSION = 0


def upgrade(version=None):
    """Migrate the database to `version` or the most recent version."""
    return IMPL.upgrade(version)


def downgrade(version=None):
    return IMPL.downgrade(version)


def version():
    return IMPL.version()


def stamp(version):
    return IMPL.stamp(version)


def revision(message, autogenerate):
    return IMPL.revision(message, autogenerate)
