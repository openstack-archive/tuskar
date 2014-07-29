# -*- encoding: utf-8 -*-
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


class StoredFile(object):
    """The StoredFile model represents the stored objects and their metadata.

    This simple model provides a common representation to be used by the
    different storage drivers when returning results.
    """

    def __init__(self, uuid, contents, store, name=None, created_at=None,
                 updated_at=None, version=None):
        """The constructor requires uuid, contents and store which are the
        common attributes in all drivers.

        The other attributes are optional

        :param uuid: The UUID for the stored object
        :type  uuid: str

        :param contents: A string containing the full contents.
        :type  contents: str

        :param store: The store where this object is located.
        :type  store: tuskar.storage.models.BaseStore

        :param name: The name of the stored object (optional)
        :type  name: str or None

        :param created_at: A datetime for when object was created (optional)
        :type  created_at: datetime.datetime

        :param updated_at: A datetime for when object was updated (optional)
        :type  updated_at: datetime.datetime

        :param version: A version number for the given object (optional)
        :type  version: int
        """

        self.uuid = uuid
        self.contents = contents
        self.store = store
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at
        self.version = version

    def __str__(self):

        name = " and name {0}".format(self.name) if self.name else ''

        return "{0} with ID {1}{2}".format(
            self.store.object_type, self.uuid, name)


class DeploymentPlan(StoredFile):
    """The DeploymentPlan model represents the deployment plan file which is
    essentially the relationship between a master template and an environment
    file.
    """

    def __init__(self, uuid, contents, store, name=None, created_at=None,
                 updated_at=None, version=None, master_template=None,
                 environment_file=None):
        """The constructor requires uuid, contents and store which are the
        common attributes in all drivers.

        The other attributes are optional

        :param uuid: The UUID for the stored object
        :type  uuid: str

        :param contents: A string containing the full contents.
        :type  contents: str

        :param store: The store where this object is located.
        :type  store: tuskar.storage.models.BaseStore

        :param name: The name of the stored object (optional)
        :type  name: str or None

        :param created_at: A datetime for when object was created (optional)
        :type  created_at: datetime.datetime

        :param updated_at: A datetime for when object was updated (optional)
        :type  updated_at: datetime.datetime

        :param version: A version number for the given object (optional)
        :type  version: int

        :param master_template: The master_template for this plan.
        :type  master_template: tuskar.storage.models.StoredFile

        :param environment_file: The environment file for this plan.
        :type  environment_file: tuskar.storage.models.StoredFile
        """

        super(DeploymentPlan, self).__init__(
            uuid, contents, store, name=name, created_at=created_at,
            updated_at=updated_at, version=version
        )

        self.master_template = master_template
        self.environment_file = environment_file

    @classmethod
    def from_stored_file(cls, stored_file, master_template=None,
                         environment_file=None):

        return DeploymentPlan(
            uuid=stored_file.uuid,
            contents=stored_file.contents,
            store=stored_file.store,
            name=stored_file.name,
            created_at=stored_file.created_at,
            updated_at=stored_file.updated_at,
            version=stored_file.version,
            master_template=master_template,
            environment_file=environment_file,
        )
