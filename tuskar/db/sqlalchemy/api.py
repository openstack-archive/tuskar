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
from sqlalchemy.exc import IntegrityError
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


def get_session():
    return db_session.get_session(sqlite_fk=True)


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):

        # The superclass __init__ is abstract and prevents the class
        # from being instantiated unless we explicitly remove that
        # here.
        pass

    def get_overcloud_roles(self):
        """Returns all overcloud roles known to Tuskar.

        :return: list of roles; empty list if none are found
        :rtype:  list of tuskar.db.sqlalchemy.models.OvercloudRole
        """

        session = get_session()
        roles = session.query(models.OvercloudRole).all()
        session.close()
        return roles

    def get_overcloud_role_by_id(self, role_id):
        """Single overcloud role query.

        :return: role if one exists with the given ID
        :rtype:  tuskar.db.sqlalchemy.models.OvercloudRole

        :raises: tuskar.common.exception.OvercloudRoleNotFound: if no
                 role with the given ID exists
        """

        session = get_session()
        try:
            query = session.query(models.OvercloudRole).filter_by(
                id=role_id)
            result = query.one()

        except NoResultFound:
            raise exception.OvercloudRoleNotFound()

        finally:
            session.close()

        return result

    def create_overcloud_role(self, overcloud_role):
        """Creates a new overcloud role in the database.

        :param overcloud_role: role instance to save
        :type  overcloud_role: tuskar.db.sqlalchemy.models.OvercloudRole

        :return: the role instance that was saved with its
                 ID populated
        :rtype:  tuskar.db.sqlalchemy.models.OvercloudRole

        :raises: tuskar.common.exception.OvercloudRoleExists: if a role
                 with the given name exists
        """
        session = get_session()
        session.begin()

        try:
            session.add(overcloud_role)
            session.commit()
            return overcloud_role

        except db_exception.DBDuplicateEntry:
            raise exception.OvercloudRoleExists(name=overcloud_role.name)

        finally:
            session.close()

    def update_overcloud_role(self, updated):
        """Updates the given overcloud role.

        :param updated: role instance containing changed values
        :type  updated: tuskar.db.sqlalchemy.models.OvercloudRole

        :return: the role instance that was saved
        :rtype:  tuskar.db.sqlalchemy.models.OvercloudRole

        :raises: tuskar.common.exception.OvercloudRoleNotFound if there
                 is no role with the given ID
        """
        existing = self.get_overcloud_role_by_id(updated.id)

        for a in ('name', 'description', 'image_name', 'flavor_id'):
            if getattr(updated, a) is not None:
                setattr(existing, a, getattr(updated, a))

        return self.create_overcloud_role(existing)

    def delete_overcloud_role_by_id(self, role_id):
        """Deletes an overcloud role from the database.

        :param role_id: database ID of the role
        :type  role_id: int

        :raises: tuskar.common.exception.OvercloudRoleNotFound if there
                 is no role with the given ID
        """
        role = self.get_overcloud_role_by_id(role_id)

        session = get_session()
        session.begin()

        try:
            session.delete(role)
            session.commit()

        except db_exception.DBError as e:
            if isinstance(e.inner_exception, IntegrityError):
                raise exception.OvercloudRoleInUse(name=role.name)
            else:
                raise

        finally:
            session.close()

    def get_overclouds(self):
        """Returns all overcloud instances from the database.

        :return: list of overcloud instances; empty list if none are found
        :rtype:  list of tuskar.db.sqlalchemy.models.Overcloud
        """

        session = get_session()
        overclouds = (
            session.query(models.Overcloud).
            options(subqueryload(models.Overcloud.attributes)).
            options(subqueryload(models.Overcloud.counts)).
            all()
        )
        session.close()
        return overclouds

    def get_overcloud_by_id(self, overcloud_id):
        """Returns a specific overcloud instance.

        :return: overcloud if one exists with the given ID
        :rtype:  tuskar.db.sqlalchemy.models.Overcloud

        :raises: tuskar.common.exception.OvercloudNotFound: if no
                 overcloud with the given ID exists
        """

        session = get_session()
        try:
            query = (
                session.query(models.Overcloud).
                options(subqueryload(models.Overcloud.attributes)).
                options(subqueryload(models.Overcloud.counts)).
                options(subqueryload('counts.overcloud_role')).
                filter_by(id=overcloud_id)
            )
            result = query.one()

        except NoResultFound:
            raise exception.OvercloudNotFound()

        finally:
            session.close()

        return result

    def create_overcloud(self, overcloud):
        """Creates a new overcloud instance to the database.

        :param overcloud: overcloud instance to save
        :type  overcloud: tuskar.db.sqlalchemy.models.Overcloud

        :return: the overcloud instance that was saved with its
                 ID populated
        :rtype:  tuskar.db.sqlalchemy.models.Overcloud

        :raises: tuskar.common.exception.OvercloudExists: if an overcloud
                 role with the given name exists
        """
        session = get_session()
        session.begin()

        try:
            session.add(overcloud)
            session.commit()

            # Reload from the database to load all of the joined table data
            overcloud = self.get_overcloud_by_id(overcloud.id)
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

        session = get_session()
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
            existing_attributes_by_key = (
                dict((a.key, a) for a in existing.attributes))

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
            existing_count_role_ids = [c.overcloud_role_id
                                       for c in existing.counts]
            existing_counts_by_role_id = (
                dict((c.overcloud_role_id, c) for c in existing.counts))

            delete_role_ids = []
            for c in updated.counts:

                # Deleted
                if c.num_nodes == 0:
                    delete_role_ids.append(c.overcloud_role_id)
                    continue

                # Updated
                if c.overcloud_role_id in existing_count_role_ids:
                    updating = existing_counts_by_role_id[c.overcloud_role_id]
                    updating.num_nodes = c.num_nodes
                    session.add(updating)
                    continue

                # New
                if c.overcloud_role_id not in existing_count_role_ids:
                    existing_counts_by_role_id[c.overcloud_role_id] = c
                    c.overcloud_id = updated.id
                    existing.counts.append(c)
                    session.add(c)
                    continue

            # Purge deleted counts
            for c in existing.counts:
                if c.overcloud_role_id in delete_role_ids:
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

        session = get_session()
        session.begin()

        try:
            session.delete(overcloud)
            session.commit()

        finally:
            session.close()
