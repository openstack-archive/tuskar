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
        resource_categories = session.query(models.ResourceCategory).all()
        session.close()
        return resource_categories

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
            query = session.query(models.ResourceCategory).filter_by(
                id=resource_category_id)
            result = query.one()

        except NoResultFound:
            raise exception.ResourceCategoryNotFound()

        finally:
            session.close()

        return result

    @staticmethod
    def save_resource_category(resource_category):
        """Saves a resource category to the database.

        If the ResourceCategory instance does not contain a value for
        its id, it will be added as a new resource category. If the id is
        present, it is treated as an update to an existing resource category.
        Therefore, updates should be made to the instance retrieved from
        one of the get_* calls and passed back to this call.

        :param resource_category: category instance to save
        :type  resource_category: tuskar.db.sqlalchemy.models.ResourceCategory

        :return: the resource category instance that was saved with its
                 ID populated

        :raises: tuskar.common.exception.ResourceCategoryExists: if a resource
                 category with the given name exists
        """
        session = db_session.get_session()
        session.begin()

        try:
            session.add(resource_category)
            session.commit()
            return resource_category

        except db_exception.DBDuplicateEntry:
            raise exception.ResourceCategoryExists(name=resource_category.name)

        finally:
            session.close()

    def delete_resource_category_by_id(self, category_id):
        """Deletes a resource category from the database.

        :param category_id: database ID of the category
        :type  category_id: int

        :raises: tuskar.common.exception.ResourceCategoryNotFound if there
                 is no category with the given ID
        """
        resource_category = self.get_resource_category_by_id(category_id)

        session = db_session.get_session()
        session.begin()

        try:
            session.delete(resource_category)
            session.commit()

        finally:
            session.close()

    @staticmethod
    def get_overclouds():
        """Returns all overcloud instances from the database.

        :return: list of overcloud instances; empty list if none are found
        :rtype:  list of tuskar.db.sqlalchemy.models.Overcloud
        """

        session = db_session.get_session()
        overclouds = session.query(models.Overcloud).\
            options(subqueryload(models.Overcloud.attributes)).\
            all()
        session.close()
        return overclouds

    @staticmethod
    def get_overcloud_by_id(overcloud_id):
        """Returns a specific overcloud instance.

        :return: overcloud if one exists with the given ID
        :rtype:  tuskar.db.sqlalchemy.models.Overcloud

        :raises: tuskar.common.exception.OvercloudNotFound: if no
                 overcloud with the given ID exists
        """

        session = db_session.get_session()
        try:
            query = session.query(models.Overcloud).\
                options(subqueryload(models.Overcloud.attributes)).\
                filter_by(id=overcloud_id)
            result = query.one()

        except NoResultFound:
            raise exception.OvercloudNotFound()

        finally:
            session.close()

        return result

    @staticmethod
    def save_overcloud(overcloud):
        """Saves the given overcloud instance to the database.

        If the Overcloud instance does not contain a value for
        its id, it will be added as a new overcloud. If the id is present,
        it is treated as an update to an existing overcloud.
        Therefore, updates should be made to the instance retrieved from
        one of the get_* calls and passed back to this call.

        :param overcloud: overcloud instance to save
        :type  overcloud: tuskar.db.sqlalchemy.models.Overcloud

        :return: the overcloud instance that was saved with its
                 ID populated

        :raises: tuskar.common.exception.OvercloudExists: if a resource
                 category with the given name exists
        """
        session = db_session.get_session()
        session.begin()

        try:
            session.add(overcloud)
            session.commit()
            return overcloud

        except db_exception.DBDuplicateEntry, e:
            if 'name' in e.columns:
                raise exception.OvercloudExists(name=overcloud.name)
            else:
                raise exception.DuplicateAttribute()

        finally:
            session.close()

    def delete_overcloud_by_id(self, overcloud_id):
        """Deletes a overcloud from the database.

        :param overcloud_id: database ID of the overcloud
        :type  overcloud_id: int

        :raises: tuskar.common.exception.OvercloudNotFound if there
                 is no overcloud with the given ID
        """
        overcloud = self.get_overcloud_by_id(overcloud_id)

        session = db_session.get_session()
        session.begin()

        try:
            session.delete(overcloud)
            session.commit()

        finally:
            session.close()
