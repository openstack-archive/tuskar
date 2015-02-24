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
from tuskar.storage.stores import TemplateExtraStore
from tuskar.storage.stores import TemplateStore
from tuskar.templates import parser


class RoleManager(object):

    def __init__(self):
        super(RoleManager, self).__init__()
        self.template_store = TemplateStore()
        self.template_extra_store = TemplateExtraStore()

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

    def retrieve_db_role_by_uuid(self, role_uuid):
        return self.template_store.retrieve(role_uuid)

    def retrieve_db_role_extra(self):
        return self.template_extra_store.list(only_latest=False)

    def template_extra_data_for_output(self, template_extra_paths):
        """Compile and return role-extra data for output as a string

            :param template_extra_paths: a list of {k,v} (name=>path)
            :type template_extra_paths: list of dict

            :return: a dict of path=>contents
            :rtype: dict

            The keys in template_extra_paths correspond to the names of stored
            role-extra data and the values are the paths at which the
            corresponding files ares expected to be. This list is returned by
            common.utils.resolve_template_extra_data for example:

                [{'extra_common_yaml': 'hieradata/common.yaml'},
                 {'extra_object_yaml': 'hieradata/object.yaml'}]

            Using this create a new dict that maps the path (values above) as
            key to the contents of the corresponding stored role-extra object
            (using the name above to retrieve it). For the example input
            above, the output would be like:

            {
                "hieradata/common.yaml": "CONTENTS",
                "hieradata/object.yaml": "CONTENTS"
            }

        """
        res = {}
        for path in template_extra_paths:
            role_extra_name = path.keys()[0]
            role_extra_path = path[role_extra_name]
            db_role_extra = self.template_extra_store.retrieve_by_name(
                role_extra_name)
            res[role_extra_path] = db_role_extra.contents
        return res

    @staticmethod
    def _role_to_tuskar_object(db_role):
        parsed = parser.parse_template(db_role.contents)
        role = models.Role(db_role.uuid, db_role.name, db_role.version,
                           parsed.description, parsed)
        return role
