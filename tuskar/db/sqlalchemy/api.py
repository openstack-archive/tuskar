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

from tuskar.common import exception
from tuskar.db import api
from tuskar.db.sqlalchemy import models
from tuskar.openstack.common.db import exception as db_exception
from tuskar.openstack.common.db.sqlalchemy import session as db_session
from tuskar.openstack.common import log


CONF = cfg.CONF
CONF.import_opt('connection',
                'tuskar.openstack.common.db.sqlalchemy.session',
                group='database')
LOG = log.getLogger(__name__)


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or db_session.get_session()
    query = session.query(model, *args)
    return query


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):

        # The superclass __init__ is abstract and prevents the class
        # from being instantiated unless we explicitly remove that
        # here.
        pass

    @staticmethod
    def get_resource_categories():
        """Returns all resource categories known to Tuskar.

        :return: list of categories; empty list if none are found
        :rtype:  list of tuskar.db.sqlalchemy.models.ResourceCategory
        """

        session = db_session.get_session()
        resource_classes = session.query(models.ResourceCategory).all()
        session.close()
        return resource_classes

    @staticmethod
    def get_resource_category_by_id(resource_category_id):
        """Single resource category query.

        :return: category if one exists with the given ID
        :rtype:  tuskar.db.sqlalchemy.models.ResourceCategory

        :raises: tuskar.common.exception.ResourceCategoryNotFound: if no
                 category with the given ID exists
        """

        session = db_session.get_session()
        try:
            query = session.query(models.ResourceCategory)
            query.filter_by(id=resource_category_id)
            result = query.one()
        except NoResultFound:
            raise exception.ResourceCategoryNotFound()
        finally:
            session.close()

        return result

    @staticmethod
    def create_resource_category(resource_category):
        """Saves a new resource category to the database.

        :param resource_category: category instance to save
        :type  resource_category: tuskar.db.sqlalchemy.models.ResourceCategory

        :raises: tuskar.common.exception.ResourceClassExists: if a resource
                 category with the given name exists
        """
        session = db_session.get_session()
        session.begin()

        try:
            session.add(resource_category)
            session.flush()

        except db_exception.DBDuplicateEntry:
            raise exception.ResourceClassExists(
                name=resource_category.name)
