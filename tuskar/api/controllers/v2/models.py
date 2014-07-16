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
Contains transfer objects for use with WSME REST APIs. The objects in this
module also contain the translations between the REST transfer objects and
the internal Tuskar domain model.
"""

import logging

from wsme import types as wtypes

LOG = logging.getLogger(__name__)


class Base(wtypes.Base):
    """Base functionality for all API models.

    This class should never be directly instantiated.
    """

    def _lookup(self, key):
        """Looks up a key, translating WSME's Unset into Python's None.

        :return: value of the given attribute; None if it is not set
        """
        value = getattr(self, key)
        if value == wtypes.Unset:
            value = None
        return value


class Role(Base):
    """Transfer object for roles."""

    uuid = str
    name = wtypes.text


class Plan(Base):
    """Transfer object for plans."""

    uuid = str
    name = wtypes.text
    roles = wtypes.ArrayType(Role)
