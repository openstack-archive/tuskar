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

from ironic.common import exception
from ironic.common import utils
from ironic.db import api
from ironic.db.sqlalchemy import models
from ironic.openstack.common.db.sqlalchemy import session as db_session
from ironic.openstack.common import log
from ironic.openstack.common import uuidutils

CONF = cfg.CONF
CONF.import_opt('connection',
                'ironic.openstack.common.db.sqlalchemy.session',
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


def add_uuid_filter(query, value):
    if utils.is_int_like(value):
        return query.filter_by(id=value)
    elif uuidutils.is_uuid_like(value):
        return query.filter_by(uuid=value)
    else:
        raise exception.InvalidUUID(uuid=value)


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    def get_blaas(self, columns):
        # FIXME(markmc): columns
        return model_query(models.Blaa).all()

    def create_blaa(self, values):
        blaa = models.Blaa()
        blaa.update(values)
        blaa.save()
        return blaa

    def get_blaa(self, blaa):
        query = model_query(models.Blaa)
        query = add_uuid_filter(query, blaa)

        try:
            result = query.one()
        except NoResultFound:
            raise exception.BlaaNotFound(blaa=blaa)

        return result

    def destroy_blaa(self, blaa):
        session = get_session()
        with session.begin():
            query = model_query(models.Blaa, session=session)
            query = add_uuid_filter(query, blaa)

            count = query.delete()
            if count != 1:
                raise exception.BlaaNotFound(blaa=blaa)

    def update_blaa(self, blaa, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Blaa, session=session)
            query = add_uuid_filter(query, blaa)

            count = query.update(values,
                                 synchronize_session='fetch')
            if count != 1:
                raise exception.BlaaNotFound(blaa=blaa)
            ref = query.one()
        return ref

    def get_sausages_by_blaa(self, blaa):
        session = get_session()

        if utils.is_int_like(blaa):
            query = session.query(models.Sausage).\
                        filter_by(blaa_id=blaa)
        else:
            query = session.query(models.Sausage).\
                        join(models.Blaa,
                             models.Sausage.blaa_id == models.Blaa.id).\
                        filter(models.Blaa.uuid == blaa)
        result = query.all()

        return result
