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

from tuskar.manager import models
from tuskar.storage.stores import TemplateStore
from tuskar.templates import parser


class RoleManager(object):

    def __init__(self):
        super(RoleManager, self).__init__()
        self.template_store = TemplateStore()

    def list_roles(self, only_latest=False):
        """Returns a list of all roles known to Tuskar.

        :param only_latest: if true, only the highest version of each role
               will be returned
        :type  only_latest: bool
        :return: list of tuskar model instances for each role
        :rtype:  [tuskar.manager.models.Role]
        """
        db_roles = self.template_store.list(only_latest=only_latest)
        roles = [self._role_to_tuskar_object(r) for r in db_roles]
        return roles

    def retrieve_role_by_uuid(self, role_uuid):
        """Returns the role with the given UUID.

        :type role_uuid: str
        :rtype: tuskar.manager.models.Role
        :raises tuskar.storage.exceptions.UnknownUUID: if there is no role with
                the given ID
        """
        db_role = self.template_store.retrieve(role_uuid)
        role = self._role_to_tuskar_object(db_role)
        return role

    @staticmethod
    def _role_to_tuskar_object(db_role):
        parsed = parser.parse_template(db_role.contents)
        role = models.Role(db_role.uuid, db_role.name, db_role.version,
                           parsed.description, parsed)
        return role
