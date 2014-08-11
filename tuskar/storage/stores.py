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

from tuskar.openstack.common import jsonutils
from tuskar.openstack.common import log
from tuskar.storage.exceptions import UnknownUUID
from tuskar.storage import get_driver
from tuskar.storage.models import DeploymentPlan

LOG = log.getLogger(__name__)


class _BaseStore(object):
    """Base class for all stores.

    This defines the basic CRUD operations and how they will be called to the
    underlying driver.
    """

    #: Object type is used to help the driver know how to store an object. For
    #: example a database may use different tables for objects and a service
    #: like swift may use different containers.
    object_type = None

    #: Flag to designate if the objects should be versioned by the driver.
    versioned = False

    def __init__(self, driver=None):
        """Given the driver to be used, set up an instance of the store. The
        driver can then be re-used between different stores.

        If the driver isn't provided, load it based on the Tuskar ini with the
        tuskar.storage.get_driver method.

        :param driver: The type of object, used for routing the storage.
        :type  driver: tuskar.storage.drivers.base.BaseDriver
        """
        self._driver = driver or get_driver(self.__class__)

    def create(self, contents):
        """Given the contents create a new file in this store and return a
        `StoredFile` instance representing it.

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile
        """

        return self._driver.create(self, None, contents)

    def retrieve(self, uuid):
        """Returns the file in this store that matches the provided UUID.

        :param uuid: UUID of the object to retrieve.
        :type  uuid: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
            found
        """
        return self._driver.retrieve(self, uuid)

    def update(self, uuid, contents):
        """Given the uuid and contents update the existing stored file
        and return an instance of StoredFile that reflects the updates.

        :param uuid: UUID of the object to update.
        :type  uuid: str

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
            found
        """
        return self._driver.update(self, uuid, contents)

    def delete(self, uuid):
        """Delete the file in this store with the matching uuid.

        :param uuid: UUID of the object to delete.
        :type  uuid: str

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
                 found
        """
        return self._driver.delete(self, uuid)

    def list(self):
        """Return a list of all the stored objects in this store.

        :return: List of StoredFile instances
        :rtype:  [tuskar.storage.models.StoredFile]
        """
        return self._driver.list(self)


class _NamedStore(_BaseStore):
    """The Named Store adds the requirement of a name attribute.

    This extends the base CRUD operations to add the requirement of a name
    where required.
    """

    def create(self, name, contents):
        """Given the name and contents create a new file and return a
        `StoredFile` instance representing it.

        When working with files that are not named, such as an EnvironmentFile
        name must be explicitly passed as None.

        :param name: name of the object to store (optional)
        :type  name: str or None

        :param contents: String containing the file contents
        :type  contents: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile

        :raises: tuskar.storage.exceptions.NameAlreadyUsed if the name is
            already in use
        """
        return self._driver.create(self, name, contents)

    def retrieve_by_name(self, name):
        """Returns the stored file for a given store that matches the provided
        name.

        :param name: name of the object to retrieve.
        :type  name: str

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile

        :raises: tuskar.storage.exceptions.UnknownName if the name can't be
            found
        """
        return self._driver.retrieve_by_name(self, name)


class _VersionedStore(_NamedStore):

    #: Flag to designate if the objects should be versioned by the driver.
    versioned = True

    def retrieve_by_name(self, name, version=None):
        """Returns the stored file for a given store that matches the provided
        name and optionally version. If the version isn't provided, the latest
        is returned.

        :param name: name of the object to retrieve.
        :type  name: str

        :param version: Version of the object to retrieve. If the version isn't
                        provided, the latest will be returned.
        :type  version: int

        :return: StoredFile instance containing the file metadata and contents
        :rtype:  tuskar.storage.models.StoredFile

        :raises: tuskar.storage.exceptions.UnknownName if the name can't be
            found
        :raises: tuskar.storage.exceptions.UnknownVersion if the version can't
            be found
        """
        return self._driver.retrieve_by_name(self, name, version)

    def list(self, only_latest=False):
        """Return a list of all the stored objects in this store.

        :param only_latest: If set to True only the latest versions of each
                            object will be returned.
        :type  only_latest: bool

        :return: List of StoredFile instances
        :rtype:  [tuskar.storage.models.StoredFile]
        """
        return self._driver.list(self, only_latest=only_latest)


class TemplateStore(_VersionedStore):
    """Template Store for Heat Orchestration TemplateStore

    Templates are named and versioned.
    """
    object_type = "template"


class MasterTemplateStore(_NamedStore):
    """Template Store for Heat Orchestration TemplateStore

    Master Templates are named and but not versioned.
    """
    object_type = "master_template"


class EnvironmentFileStore(_BaseStore):
    """Environment File for Heat environment files.

    Environment Files are not named and don't contain versions.
    """
    object_type = "environment"


class DeploymentPlanStore(_NamedStore):
    """Deployment Plan Store

    Deployment plans are named but not versioned.
    """
    object_type = "deployment_plan"

    def __init__(self, master_template_store=None, environment_store=None,
                 *args, **kwargs):
        super(DeploymentPlanStore, self).__init__(*args, **kwargs)

        self._template_store = master_template_store or MasterTemplateStore()
        self._env_file_store = environment_store or EnvironmentFileStore()

    def _serialise(self, master_template, environment_file):
        """Given the master_template and environment_file UUID's create a
        simple dictionary representation of the Plan and serialise it to JSON.

        :param master_template: Master template UUID
        :type  master_template: str

        :param environment_file: Environment File UUID.
        :type  environment_file: str

        :return: JSON String
        :rtype:  str
        """

        plan = {
            "master_template_uuid": master_template,
            "environment_file_uuid": environment_file
        }

        return jsonutils.dumps(plan, sort_keys=True)

    def _deserialise(self, plan_stored_file):
        """Load the Plan from a JSON string containing the master template
        UUID and the environment file UUID.

        :param plan_stored_file: Stored File model instance
        :type  plan_stored_file: tuskar.storage.models.StoredFile

        :return: Deployment Plan model instance
        :rtype: tuskar.storage.models.DeploymentPlan
        """

        metadata = jsonutils.loads(plan_stored_file.contents)

        plan_uuid = plan_stored_file.uuid
        template_uuid = metadata['master_template_uuid']
        env_uuid = metadata['environment_file_uuid']

        try:
            master = self._template_store.retrieve(template_uuid)
        except UnknownUUID:
            LOG.warn("Deployment Plan {0} had a relation to Template {1} "
                     "which doesn't exist.".format(plan_uuid, template_uuid))
            master = None

        try:
            env = self._env_file_store.retrieve(env_uuid)
        except UnknownUUID:
            LOG.warn("Deployment Plan {0} had a relation to Environment {1} "
                     "which doesn't exist.".format(plan_uuid, env_uuid))
            env = None

        return DeploymentPlan.from_stored_file(plan_stored_file,
                                               master_template=master,
                                               environment_file=env)

    def _create_empty_template(self, name):
        empty_file = ""
        master_template = self._template_store.create(name, empty_file)
        return master_template

    def _create_empty_environment(self):
        empty_file = ""
        environment_file = self._env_file_store.create(empty_file)
        return environment_file

    def create(self, name, master_template_uuid=None, environment_uuid=None):
        """Given the UUID's for a template and environment, create the Plan
        relationship between the two. If one or either are not provided then
        a new, empty template or environment will be created for them.

        :param master_template_uuid: Template UUID
        :type  master_template_uuid: str or None

        :param environment_uuid: environment UUID
        :type  environment_uuid: str or None

        :return: DeploymentPlan instance containing the relationship
        :rtype:  tuskar.storage.models.DeploymentPlan

        :raises: tuskar.storage.exceptions.NameAlreadyUsed if the name is
            already in use
        """

        if master_template_uuid is None:
            master_template = self._create_empty_template(name)
            master_template_uuid = master_template.uuid

        if environment_uuid is None:
            environment = self._create_empty_environment()
            environment_uuid = environment.uuid

        contents = self._serialise(master_template_uuid, environment_uuid)
        plan_file = super(DeploymentPlanStore, self).create(name, contents)
        return self._deserialise(plan_file)

    def retrieve(self, uuid):
        """Returns the deployment plan relationship for the given UUID.

        :param uuid: Deployment Plan UUID
        :type  uuid: str

        :return: DeploymentPlan instance containing the relationship
        :rtype:  tuskar.storage.models.DeploymentPlan

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
            found
        """
        plan_file = super(DeploymentPlanStore, self).retrieve(uuid)
        return self._deserialise(plan_file)

    def update(self, uuid, master_template_uuid=None, environment_uuid=None):
        """Given the UUID's for a template and environment, update the Plan
        relationship. If they are not provided, then the UUID will not be
        updated.

        :param uuid: Deployment Plan UUID
        :type  uuid: str

        :param master_template_uuid: Template UUID
        :type  master_template_uuid: str or None

        :param environment_uuid: environment UUID
        :type  environment_uuid: str or None

        :return: DeploymentPlan instance containing the relationship
        :rtype:  tuskar.storage.models.DeploymentPlan

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
            found
        :raises: ValueError if neither master_template_uuid or environment_uuid
            are provided.
        """

        plan = self.retrieve(uuid)

        if master_template_uuid is None and environment_uuid is None:
            raise ValueError("Either the master_template_uuid and/or "
                             "environment_uuid must be provided for an update")

        if master_template_uuid is None:
            master_template_uuid = plan.master_template.uuid

        if environment_uuid is None:
            environment_uuid = plan.environment_file.uuid

        contents = self._serialise(master_template_uuid, environment_uuid)
        plan_file = super(DeploymentPlanStore, self).update(uuid, contents)
        return self._deserialise(plan_file)

    def update_master_template(self, plan_uuid, master_template_contents):
        """Given the plan UUID and the master template contents, update the
        template and return the updated DeploymentPlan.

        :param plan_uuid: Deployment Plan UUID
        :type  plan_uuid: str

        :param master_template_contents: Master Template contents
        :type  master_template_contents: str

        :return: DeploymentPlan instance containing the relationship
        :rtype:  tuskar.storage.models.DeploymentPlan

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
            found
        """

        # Fetch the plan, this is primarily to get the master template UUID.
        plan = self.retrieve(plan_uuid)
        template_uuid = plan.master_template.uuid

        # Update the template contents
        updated_template = self._template_store.update(
            template_uuid, master_template_contents)

        # Manually update the plan, to avoid having to refetch it from the
        # store as we know nothing else has changed.
        plan.master_template = updated_template

        return plan

    def update_environment(self, plan_uuid, environment_contents):
        """Given the plan UUID and the environment contents, update the
        environment and return the updated Deployment Plan.

        :param plan_uuid: Deployment Plan UUID
        :type  plan_uuid: str

        :param environment_contents: Environment contents
        :type  environment_contents: str

        :return: DeploymentPlan instance containing the relationship
        :rtype:  tuskar.storage.models.DeploymentPlan

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
            found
        """

        # Fetch the plan, this is primarily to get the environment UUID.
        plan = self.retrieve(plan_uuid)
        environment_uuid = plan.environment_file.uuid

        # Update the environment contents
        updated_env = self._env_file_store.update(
            environment_uuid, environment_contents)

        # Manually update the plan, to avoid having to refetch it from the
        # store as we know nothing else has changed.
        plan.environment_file = updated_env

        return plan

    def list(self):
        """Return a list of all the deployment plans in this store.

        :return: List of DeploymentPlan instances
        :rtype:  [tuskar.storage.models.DeploymentPlan]
        """
        stored_files = super(DeploymentPlanStore, self).list()
        return [self._deserialise(stored_file) for stored_file in stored_files]

    def retrieve_by_name(self, name):
        """Returns the deployment plan for a given store that matches the
        provided name.

        :param name: name of the object to retrieve.
        :type  name: str

        :return: DeploymentPlan instance containing the relationship
        :rtype:  tuskar.storage.models.DeploymentPlan

        :raises: tuskar.storage.exceptions.UnknownName if the name can't be
            found
        """
        stored_file = super(DeploymentPlanStore, self).retrieve_by_name(name)
        return self._deserialise(stored_file)

    def delete(self, uuid):
        """Delete the DeploymentPlan and it's related MasterTemplate end
        EnvironmentFile. If the MasterTemplate or EnvironmentFile can't be
        found, the exceptions will be ignored and the DeploymentPlan will still
        be deleted.

        :param uuid: UUID of the DeploymentPlan to delete.
        :type  uuid: str

        :raises: tuskar.storage.exceptions.UnknownUUID if the UUID can't be
            found for the DeploymentPlan.
        """

        plan = self.retrieve(uuid)

        if plan.master_template:
            self._template_store.delete(plan.master_template.uuid)

        if plan.environment_file:
            self._env_file_store.delete(plan.environment_file.uuid)

        return self._driver.delete(self, uuid)
