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
from tuskar.manager import name_utils
from tuskar.storage.stores import DeploymentPlanStore
from tuskar.storage.stores import EnvironmentFileStore
from tuskar.storage.stores import MasterTemplateStore
from tuskar.storage.stores import TemplateStore
from tuskar.templates import composer
from tuskar.templates import namespace as ns_utils
from tuskar.templates import parser
from tuskar.templates import plan


class PlansManager(object):

    def __init__(self):
        super(PlansManager, self).__init__()
        self.plan_store = DeploymentPlanStore()
        self.template_store = TemplateStore()
        self.master_template_store = MasterTemplateStore()
        self.environment_store = EnvironmentFileStore()

    def create_plan(self, name, description):
        """Creates a new plan, persisting it to Tuskar's storage backend.

        :type name: str
        :type description: str
        :return: domain model instance of the created plan
        :rtype: tuskar.manager.models.DeploymentPlan
        :raises tuskar.storage.exceptions.NameAlreadyUsed: if there is a plan
                with the given name
        """

        # Create the plan using the template generation code first to
        # stub out the master template and environment files correctly.
        new_plan = plan.DeploymentPlan(description=description)

        # Save the newly created master template and environment to the
        # storage layer so they can be associated with the plan.
        master_template_contents = composer.compose_template(
            new_plan.master_template
        )
        master_template_file = self.master_template_store.create(
            name_utils.master_template_filename(name),
            master_template_contents,
        )

        environment_contents = composer.compose_environment(
            new_plan.environment
        )
        environment_file = self.environment_store.create(
            environment_contents
        )

        # Create the plan in storage, seeding it with the stored files for
        # the template and environment.
        db_plan = self.plan_store.create(
            name,
            master_template_uuid=master_template_file.uuid,
            environment_uuid=environment_file.uuid,
        )

        # Return the created plan.
        created_plan = self.retrieve_plan(db_plan.uuid)
        return created_plan

    def delete_plan(self, plan_uuid):
        """Deletes an existing plan.

        :type plan_uuid: str
        :raises tuskar.storage.exceptions.UnknownUUID: if there is no plan
                with the given UUID
        """
        self.plan_store.delete(plan_uuid)

    def add_role_to_plan(self, plan_uuid, role_uuid):
        """Adds a role to the given plan, storing the changes in Tuskar's
        storage.

        :type plan_uuid: str
        :type role_uuid: str
        :return: updated plan model instance
        :rtype: tuskar.manager.models.DeploymentPlan
        :raises tuskar.storage.exceptions.UnknownUUID: if either the plan
                or the role cannot be found
        """

        # Load the plan and role from storage
        db_plan = self.plan_store.retrieve(plan_uuid)
        db_role = self.template_store.retrieve(role_uuid)

        # Parse the plan and role template into template objects.
        deployment_plan = self._plan_to_template_object(db_plan)
        role_template = self._role_to_template_object(db_role)

        # Use the combination logic to perform the addition.
        role_namespace = name_utils.generate_role_namespace(db_role.name,
                                                            db_role.version)
        template_filename = name_utils.role_template_filename(db_role.name,
                                                              db_role.version)
        deployment_plan.add_template(role_namespace, role_template,
                                     template_filename)

        # Save the updated plan.
        updated = self._save_updated_plan(plan_uuid, deployment_plan)

        return updated

    def remove_role_from_plan(self, plan_uuid, role_uuid):
        """Removes a role from the given plan.

        :type plan_uuid: str
        :type role_uuid: str
        :raise tuskar.storage.exceptions.UnknownUUID: if the plan or role
               doesn't exist
        """

        # Load the objects from storage.
        db_plan = self.plan_store.retrieve(plan_uuid)
        db_role = self.template_store.retrieve(role_uuid)

        # Parse the plan into template objects.
        deployment_plan = self._plan_to_template_object(db_plan)

        # Delete the role from the plan by it's namespace.
        role_namespace = name_utils.generate_role_namespace(db_role.name,
                                                            db_role.version)
        deployment_plan.remove_template(role_namespace)

        # Save the updated plan.
        updated = self._save_updated_plan(plan_uuid, deployment_plan)

        return updated

    def retrieve_plan(self, plan_uuid):
        """Loads the given plan.

        :type plan_uuid: str
        :rtype: tuskar.manager.models.DeploymentPlan
        :raises tuskar.storage.exceptions.UnknownUUID: if there is no plan
                with the given UUID
        """

        # Load the plan from the database.
        db_plan = self.plan_store.retrieve(plan_uuid)

        # Parse the plan into the template model.
        master_template = parser.parse_template(
            db_plan.master_template.contents
        )
        environment = parser.parse_environment(
            db_plan.environment_file.contents
        )

        # Create the Tuskar model for the plan.
        deployment_plan = models.DeploymentPlan(
            plan_uuid,
            db_plan.name,
            master_template.description,
            created_at=db_plan.created_at,
            updated_at=db_plan.updated_at,
        )

        roles = self._find_roles(environment)
        deployment_plan.add_roles(*roles)

        params = self._find_parameters(master_template, environment)
        deployment_plan.add_parameters(*params)

        return deployment_plan

    def list_plans(self):
        """Returns a list of all plans stored in Tuskar.

        :return: list of plan instances; empty list if there are no plans
        :rtype: [tuskar.manager.models.DeploymentPlan]
        """

        # Given the expected number of plans being managed by Tuskar (in the
        # tens), this should be sufficient. If our scale gets larger, we may
        # need a smarter batch operation here than simply iterating over the
        # list of all plans. jdob, Aug 7, 2014

        plan_uuids = [p.uuid for p in self.plan_store.list()]
        plans = [self.retrieve_plan(p) for p in plan_uuids]

        return plans

    def set_parameter_values(self, plan_uuid, params):
        """Sets the values for a plan's parameters.

        :type plan_uuid: str
        :type params: [tuskar.manager.models.ParameterValue]

        :return: plan instance with the updated values
        :rtype:  tuskar.manager.models.DeploymentPlan
        """

        # Load the plan from the database.
        db_plan = self.plan_store.retrieve(plan_uuid)

        # Save the values to the parsed environment.
        environment = parser.parse_environment(
            db_plan.environment_file.contents
        )

        for param_value in params:
            p = environment.find_parameter_by_name(param_value.name)
            p.value = param_value.value

        # Save the updated environment.
        env_contents = composer.compose_environment(environment)
        self.plan_store.update_environment(plan_uuid, env_contents)

        updated_plan = self.retrieve_plan(plan_uuid)
        return updated_plan

    def _find_roles(self, environment):
        """Returns a list of roles for a plan (identified by the given
        environment).

        :type environment: tuskar.templates.heat.Environment
        :return: list of role instances; empty list if none are in the
                 environment
        :rtype: [tuskar.manager.models.Role]
        """

        def load_role(entry):
            # Figure out the role name/version for the given entry.
            namespace = ns_utils.remove_resource_alias_namespace(entry.alias)
            name, version = name_utils.parse_role_namespace(namespace)

            # Load the role from the database and parse into the
            # template objects.
            db_role = self.template_store.retrieve_by_name(name, int(version))
            role = self._role_to_template_object(db_role)

            # Convert to the Tuskar domain model.
            tuskar_role = models.Role(db_role.uuid, name, version,
                                      role.description, role)
            return tuskar_role

        roles = [load_role(e) for e in environment.registry_entries]
        return roles

    @staticmethod
    def _find_parameters(template, environment):
        """Returns a list of parameters for a plan. The parameters will contain
        both metadata about the parameter itself (name, label, description,
        etc.) as well as it's current value for the plan.

        :type template: tuskar.templates.heat.Template
        :type environment: tuskar.templates.heat.Environment
        :return: list of parameter instances; empty list if there are no
                 parameters in the plan
        :rtype: [tuskar.manager.models.PlanParameter]
        """

        def generate_param(p):
            env_param = environment.find_parameter_by_name(p.name)
            return models.PlanParameter(
                p.name, env_param.value, p.param_type,
                p.description, p.label, p.default, p.hidden
            )

        params = [generate_param(tp) for tp in template.parameters]
        return params

    @staticmethod
    def _plan_to_template_object(db_plan):
        master_template = parser.parse_template(
            db_plan.master_template.contents
        )
        environment = parser.parse_environment(
            db_plan.environment_file.contents
        )
        deployment_plan = plan.DeploymentPlan(master_template=master_template,
                                              environment=environment)
        return deployment_plan

    @staticmethod
    def _role_to_template_object(db_role):
        role_template = parser.parse_template(db_role.contents)
        return role_template

    def _save_updated_plan(self, plan_uuid, deployment_plan):
        new_template_contents = composer.compose_template(
            deployment_plan.master_template
        )
        new_env_contents = composer.compose_environment(
            deployment_plan.environment
        )

        self.plan_store.update_master_template(plan_uuid,
                                               new_template_contents)
        self.plan_store.update_environment(plan_uuid,
                                           new_env_contents)

        # Retrieve and return the updated plan
        updated_plan = self.retrieve_plan(plan_uuid)
        return updated_plan
