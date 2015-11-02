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

import datetime
import logging

import six
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



class PlanFile(Base):
    contents = wtypes.text
    meta = {str: str}

    @classmethod
    def from_dict(cls, plan_file_dict):
        """Translates from a dict
        """
        plan_file = cls(**{
            'contents': plan_file_dict['contents'],
            'meta': plan_file_dict['meta'],
        })
        return plan_file

    
class Plan(Base):
    plan_files = {str: PlanFile}

    @classmethod
    def from_dict(cls, plan_files):
        """Translates from a dict
        """
        transfer_plan_files = {}
        for key, value in plan_files.iteritems():
            transfer_plan_files[key] = PlanFile.from_dict(value)

        plan = cls(**{
            'plan_files': transfer_plan_files,
        })
        return plan
