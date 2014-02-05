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
    def create_resource_category(resource_category):
        """Creates a new resource category in the database.

        :param resource_category: category instance to save
        :type  resource_category: tuskar.db.sqlalchemy.models.ResourceCategory

        :return: the resource category instance that was saved with its
                 ID populated
        :rtype:  tuskar.db.sqlalchemy.models.ResourceCategory

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

    def update_resource_category(self, updated):
        """Updates the given resource category.

        :param updated: category instance containing changed values
        :type  updated: tuskar.db.sqlalchemy.models.ResourceCategory

        :return: the resource category instance that was saved
        :rtype:  tuskar.db.sqlalchemy.models.ResourceCategory

        :raises: tuskar.common.exception.ResourceCategoryNotFound if there
                 is no category with the given ID
        """
        existing = self.get_resource_category_by_id(updated.id)

        for a in ('name', 'description', 'image_name', 'flavor_id'):
            if getattr(updated, a) is not None:
                setattr(existing, a, getattr(updated, a))

        return self.create_resource_category(existing)

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
            options(subqueryload(models.Overcloud.counts)).\
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
                options(subqueryload(models.Overcloud.counts)).\
                filter_by(id=overcloud_id)
            result = query.one()

        except NoResultFound:
            raise exception.OvercloudNotFound()

        finally:
            session.close()

        return result

    @staticmethod
    def create_overcloud(overcloud):
        """Creates a new overcloud instance to the database.

        :param overcloud: overcloud instance to save
        :type  overcloud: tuskar.db.sqlalchemy.models.Overcloud

        :return: the overcloud instance that was saved with its
                 ID populated
        :rtype:  tuskar.db.sqlalchemy.models.Overcloud

        :raises: tuskar.common.exception.OvercloudExists: if a resource
                 category with the given name exists
        """
        session = db_session.get_session()
        session.begin()

        try:
            session.add(overcloud)
            session.commit()
            return overcloud

        except db_exception.DBDuplicateEntry as e:
            if 'name' in e.columns:
                raise exception.OvercloudExists(name=overcloud.name)
            else:
                raise exception.DuplicateAttribute()

        finally:
            session.close()

    def update_overcloud(self, updated):
        """Updates the configuration of an existing overcloud.

        The specified parameter is an instance of the domain model with
        the changes to be made. Updating follows the given rules:
        - The updated overcloud must include the ID of the overcloud
          being updated.
        - Any direct attributes on the overcloud that are *not* being changed
          should have their values set to None.
        - For attributes and counts, only differences are specified according
          to the following rules:
          - New items are specified in the updated object's lists
          - Updated items are specified in the updated object's lists with
            the new value and existing key
          - Removed items are specified in the updated object's lists with
            a value of None (zero in the case of a count).
          - Unchanged items are *not* specified.

        :param updated: overcloud instance containing changed values
        :type  updated: tuskar.db.sqlalchemy.models.Overcloud

        :return: the overcloud instance that was saved
        :rtype:  tuskar.db.sqlalchemy.models.Overcloud

        :raises: tuskar.common.exception.OvercloudNotFound if there
                 is no overcloud with the given ID
        """

        existing = self.get_overcloud_by_id(updated.id)

        session = db_session.get_session()
        session.begin()

        try:
            # First class attributes on the overcloud
            for name in ('stack_id', 'name', 'description'):
                new_value = getattr(updated, name)
                if new_value is not None:
                    setattr(existing, name, new_value)

            self._update_overcloud_attributes(existing, session, updated)
            self._update_overcloud_counts(existing, session, updated)

            # Save the modified object
            session.add(existing)
            session.commit()

            return existing

        finally:
            session.close()

    @staticmethod
    def _update_overcloud_attributes(existing, session, updated):
        if updated.attributes is not None:
            existing_keys = [a.key for a in existing.attributes]
            existing_attributes_by_key = \
                dict((a.key, a) for a in existing.attributes)

            delete_keys = []
            for a in updated.attributes:

                # Deleted
                if a.value is None:
                    delete_keys.append(a.key)
                    continue

                # Updated
                if a.key in existing_keys:
                    updating = existing_attributes_by_key[a.key]
                    updating.value = a.value
                    session.add(updating)
                    continue

                # Added
                if a.key not in existing_keys:
                    existing_attributes_by_key[a.key] = a
                    a.overcloud_id = updated.id
                    existing.attributes.append(a)
                    session.add(a)
                    continue

            # Purge deleted attributes
            for a in existing.attributes:
                if a.key in delete_keys:
                    existing.attributes.remove(a)
                    session.delete(a)

    @staticmethod
    def _update_overcloud_counts(existing, session, updated):
        if updated.counts is not None:
            existing_count_cat_ids = [c.resource_category_id
                                      for c in existing.counts]
            existing_counts_by_cat_id = \
                dict((c.resource_category_id, c) for c in existing.counts)

            delete_category_ids = []
            for c in updated.counts:

                # Deleted
                if c.num_nodes == 0:
                    delete_category_ids.append(c.resource_category_id)
                    continue

                # Updated
                if c.resource_category_id in existing_count_cat_ids:
                    updating = \
                        existing_counts_by_cat_id[c.resource_category_id]
                    updating.num_nodes = c.num_nodes
                    session.add(updating)
                    continue

                # New
                if c.resource_category_id not in existing_count_cat_ids:
                    existing_counts_by_cat_id[c.resource_category_id] = c
                    c.overcloud_id = updated.id
                    existing.counts.append(c)
                    session.add(c)
                    continue

            # Purge deleted counts
            for c in existing.counts:
                if c.resource_category_id in delete_category_ids:
                    existing.counts.remove(c)
                    session.delete(c)

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
