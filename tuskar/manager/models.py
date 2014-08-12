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


class Role(object):

    def __init__(self, uuid, name, version, description, template):
        super(Role, self).__init__()

        self.uuid = uuid
        self.name = name
        self.version = version
        self.description = description
        self.template = template


class DeploymentPlan(object):

    def __init__(self, uuid, name, description,
                 created_at=None, updated_at=None):
        super(DeploymentPlan, self).__init__()

        self.uuid = uuid
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at

        self._roles = []  # list of Role
        self._parameters = []  # list of PlanParameter

    @property
    def roles(self):
        return tuple(self._roles)

    @property
    def parameters(self):
        return tuple(self._parameters)

    def add_roles(self, *role):
        """Adds one or more roles to the plan.

        :type role: tuskar.manager.models.Role
        """
        for r in role:
            self._roles.append(r)

    def add_parameters(self, *parameters):
        """Adds one or more parameters to the plan.

        :type parameters: tuskar.manager.models.PlanParameter
        """
        for p in parameters:
            self._parameters.append(p)


class PlanParameter(object):

    def __init__(self, name, value, param_type, description,
                 label, default, hidden):
        super(PlanParameter, self).__init__()
        self.name = name
        self.value = value
        self.param_type = param_type
        self.description = description
        self.label = label
        self.default = default
        self.hidden = hidden
