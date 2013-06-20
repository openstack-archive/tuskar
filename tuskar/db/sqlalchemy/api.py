# vim: tabstop=4 shiftwidth=4 softtabstop=4
# -*- encoding: utf-8 -*-
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""SQLAlchemy storage backend."""

from oslo.config import cfg

# TODO(deva): import MultipleResultsFound and handle it appropriately
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import subqueryload

from tuskar.common import exception
from tuskar.common import utils
from tuskar.db import api
from tuskar.db.sqlalchemy import models
from tuskar.openstack.common.db.sqlalchemy import session as db_session
from tuskar.openstack.common import log
from tuskar.openstack.common import uuidutils

CONF = cfg.CONF
CONF.import_opt('connection',
                'tuskar.openstack.common.db.sqlalchemy.session',
                group='database')

LOG = log.getLogger(__name__)

get_engine = db_session.get_engine
get_session = db_session.get_session


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    def get_racks(self, columns):
        session = get_session()
        return session.query(models.Rack).options(
                    subqueryload('capacities')
                ).all()

    def get_rack(self, rack_id):
        session = get_session()
        try:
            result = session.query(models.Rack).options(
                    subqueryload('capacities')
                    ).filter_by(id=rack_id).one()
        except NoResultFound:
            raise exception.RackNotFound(rack=rack_id)

        return result

    def create_rack(self, values):
        rack = models.Rack()
        if 'capacities' in values:
            for capacity in values.pop('capacities'):
                c = models.Capacity(name=capacity.name, value=capacity.value)
                c.save()
                rack.capacities.append(c)
        rack.update(values)
        rack.save()
        return rack

    def get_resource_classes(self, columns):
        session = get_session()
        return session.query(models.ResourceClass).all()

    def create_resource_class(self, values):
        rc = models.ResourceClass()
        # FIXME: This should be DB transaction ;-)
        #
        rc.update(values)
        rc.save()
        return rc
