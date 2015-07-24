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

from oslo_log import log as logging
import six
from wsme import types as wtypes

from tuskar.api.controllers.v2 import types as v2types
from tuskar.manager import models as manager_models

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

    uuid = wtypes.text
    name = wtypes.text
    version = int
    description = wtypes.text

    @classmethod
    def from_tuskar_model(cls, role):
        """Translates from the Tuskar domain model.

        :type role: tuskar.manager.models.Role
        """
        r = cls(**{
            'uuid': role.uuid,
            'name': role.name,
            'version': role.version,
            'description': role.description
        })
        return r


class ParameterConstraint(Base):

    constraint_type = wtypes.text
    definition = v2types.MultiType(list, dict, wtypes.text)
    description = wtypes.text

    @classmethod
    def from_tuskar_model(cls, constraint):
        return cls(**{'constraint_type': constraint.constraint_type,
                      'definition': constraint.definition,
                      'description': constraint.description})


class PlanParameter(Base):

    name = wtypes.text
    label = wtypes.text
    default = v2types.MultiType(wtypes.text, six.integer_types, list, dict)
    description = wtypes.text
    hidden = bool
    value = v2types.MultiType(wtypes.text, six.integer_types, list, dict)
    constraints = [ParameterConstraint]
    parameter_type = wtypes.text

    @classmethod
    def from_tuskar_model(cls, param):
        """Translates from the Tuskar domain model.

        :type param: tuskar.manager.models.PlanParameter
        """
        constraints = [ParameterConstraint.from_tuskar_model(c)
                       for c in param.constraints]
        p = cls(**{
            'name': param.name,
            'label': param.label,
            'default': param.default,
            'description': param.description,
            'hidden': param.hidden,
            'value': param.value,
            'constraints': constraints,
            'parameter_type': param.param_type
        })
        return p


class Plan(Base):

    uuid = wtypes.text
    name = wtypes.text
    description = wtypes.text
    created_at = datetime.datetime
    updated_at = datetime.datetime
    roles = [Role]
    parameters = [PlanParameter]

    @classmethod
    def from_tuskar_model(cls, plan):
        """Translates from the Tuskar domain model.

        :type plan: tuskar.manager.models.DeploymentPlan
        """
        roles = [Role.from_tuskar_model(r) for r in plan.roles]
        params = [PlanParameter.from_tuskar_model(p) for p in plan.parameters]

        p = cls(**{
            'uuid': plan.uuid,
            'name': plan.name,
            'description': plan.description,
            'created_at': plan.created_at,
            'updated_at': plan.updated_at,
            'roles': roles,
            'parameters': params,
        })
        return p


class ParameterValue(Base):

    name = wtypes.text
    value = wtypes.text

    @classmethod
    def from_tuskar_model(cls, param_value):
        """Translates from the Tuskar domain model.

        :type param_value: tuskar.manager.models.ParameterValue
        """
        p = cls(**{
            'name': param_value.name,
            'value': param_value.value,
        })
        return p

    def to_tuskar_model(self):
        """Translates into the Tuskar domain model.

        :rtype: tuskar.manager.models.ParameterValue
        """
        p = manager_models.ParameterValue(self.name, self.value)
        return p
