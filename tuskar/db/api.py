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
"""
Base classes for storage engines
"""

import abc

from tuskar.openstack.common.db import api as db_api

_BACKEND_MAPPING = {'sqlalchemy': 'tuskar.db.sqlalchemy.api'}
IMPL = db_api.DBAPI(backend_mapping=_BACKEND_MAPPING)


def get_instance():
    """Return a DB API instance."""
    return IMPL


class Connection(object):
    """Base class for storage system connections."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    @abc.abstractmethod
    def get_blaas(self, columns):
        """Return a list of dicts of all blaas.

        :param columns: List of columns to return.
        """

    @abc.abstractmethod
    def create_blaa(self, values):
        """Create a new blaa.

        :param values: A dict describing a blaa.
                        {
                         'uuid': uuidutils.generate_uuid(),
                         'description': 'foo',
                        }
        :returns: A blaa.
        """

    @abc.abstractmethod
    def get_blaa(self, blaa):
        """Return a blaa.

        :param node: The id or uuid of a blaa.
        :returns: A blaa.
        """

    @abc.abstractmethod
    def destroy_blaa(self, node):
        """Destroy a blaa.

        :param node: The id or uuid of a blaa.
        """

    @abc.abstractmethod
    def update_blaa(self, blaa, values):
        """Update properties of a blaa.

        :param node: The id or uuid of a blaa.
        :param values: Dict of values to update.
                       May be a partial list. For example:

                       {
                        'description': 'foobar',
                       }
        :returns: A blaa.
        """

    @abc.abstractmethod
    def get_sausages_by_blaa(self, blaa):
        """List all the sausages for a given blaa.

        :param node: The id or uuid of a blaa.
        :returns: A list of sausages.
        """
