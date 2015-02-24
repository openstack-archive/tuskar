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

import logging

from tuskar.common import exception
from tuskar.common import utils
from tuskar.manager import models
from tuskar.manager import name_utils
from tuskar.manager.role import RoleManager
from tuskar.storage.exceptions import UnknownName
from tuskar.storage.load_roles import RESOURCE_REGISTRY_NAME
from tuskar.storage.load_roles import role_name_from_path
from tuskar.storage.stores import DeploymentPlanStore
from tuskar.storage.stores import EnvironmentFileStore
from tuskar.storage.stores import MasterSeedStore
from tuskar.storage.stores import MasterTemplateStore
from tuskar.storage.stores import ResourceRegistryMappingStore
from tuskar.storage.stores import ResourceRegistryStore
from tuskar.storage.stores import TemplateExtraStore
from tuskar.storage.stores import TemplateStore
from tuskar.templates import composer
from tuskar.templates import namespace as ns_utils
from tuskar.templates import parser
from tuskar.templates import plan
from tuskar.templates import template_seed
from tuskar.templates.heat import RegistryEntry


LOG = logging.getLogger(__name__)
MASTER_SEED_NAME = '_master_seed'


class PlansManager(object):

    def __init__(self):
        super(PlansManager, self).__init__()
        self.plan_store = DeploymentPlanStore()
        self.seed_store = MasterSeedStore()
        self.registry_store = ResourceRegistryStore()
        self.registry_mapping_store = ResourceRegistryMappingStore()
        self.template_store = TemplateStore()
        self.template_extra_store = TemplateExtraStore()
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

        # See if a master seed template has been set.
        try:
            db_master_seed = self.seed_store.retrieve_by_name(MASTER_SEED_NAME)
            master_seed = parser.parse_template(db_master_seed.contents)
        except UnknownName:
            master_seed = None
            special_properties = None

        if master_seed is not None:
            try:
                db_registry_env = self.registry_store.retrieve_by_name(
                    RESOURCE_REGISTRY_NAME).contents
            except UnknownName:
                LOG.error("Could not load resource_registry. Make sure you "
                          "pass --resource-registry to tuskar-load-roles.")
                raise
            parsed_registry_env = parser.parse_environment(db_registry_env)
            registry = dict((role_name_from_path(e.filename), e.alias)
                            for e in parsed_registry_env.registry_entries)
            special_properties = template_seed.get_property_map_for_role(
                master_seed, registry[db_role.name])

        # Use the combination logic to perform the addition.
        role_namespace = name_utils.generate_role_namespace(db_role.name,
                                                            db_role.version)
        template_filename = name_utils.role_template_filename(db_role.name,
                                                              db_role.version)
        deployment_plan.add_template(role_namespace, role_template,
                                     template_filename,
                                     override_properties=special_properties)

        # If there is a master seed, add its top-level elements to the plan.
        # These calls are idempotent, so it's safe to call each time a role
        # is added.
        if master_seed is not None:
            template_seed.add_top_level_parameters(
                master_seed,
                deployment_plan.master_template,
                deployment_plan.environment)
            template_seed.add_top_level_resources(
                master_seed, deployment_plan.master_template)
            template_seed.add_top_level_outputs(
                master_seed, deployment_plan.master_template)

            try:
                role_type = registry[db_role.name]
            except KeyError:
                LOG.error(
                    "Role '%s' not found in seed template." % db_role.name)
                raise
            seed_role = template_seed.find_role_from_type(
                master_seed.resources, role_type)
            if seed_role is None:
                LOG.error(
                    "Role '%s' of type '%s' not found in seed template." %
                    (db_role.name, role_type))
                raise ValueError(db_role.name)

            # These calls are idempotent, but must be called on each role as
            # new references may have been added.
            template_seed.update_role_resource_references(
                deployment_plan.master_template,
                seed_role,
                plan.generate_group_id(role_namespace))

            template_seed.update_role_property_references(
                deployment_plan.master_template,
                seed_role,
                role_namespace)

            # Update environment file to add top level mappings
            reg_mapping = self.registry_mapping_store.list()

            environment = deployment_plan.environment
            for entry in parsed_registry_env.registry_entries:
                # check if registry_mapping is in database, if so add to
                # environment (later will become environment.yaml)
                if any(x.name == entry.filename for x in reg_mapping):
                    additem = RegistryEntry(entry.alias, entry.filename)
                    environment.add_registry_entry(additem, iset=True)

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

        non_existent_params = []
        for param_value in params:
            p = environment.find_parameter_by_name(param_value.name)
            if p:
                p.value = param_value.value
            else:
                non_existent_params.append(param_value.name)

        if non_existent_params:
            param_names = ', '.join(non_existent_params)
            LOG.error(
                'There are no parameters named %(param_names)s'
                ' in plan %(plan_uuid)s.' %
                {'param_names': param_names, 'plan_uuid': plan_uuid})
            raise exception.PlanParametersNotExist(
                plan_uuid=plan_uuid,
                param_names=param_names
            )

        # Save the updated environment.
        env_contents = composer.compose_environment(environment)
        self.plan_store.update_environment(plan_uuid, env_contents)

        updated_plan = self.retrieve_plan(plan_uuid)
        return updated_plan

    def package_templates(self, plan_uuid):
        """Packages and returns all of the templates related to the given plan.
        The returned dictionary is keyed by filename and contains the contents
        of that file (a template or an environment file).

        :type plan_uuid: str

        :return: mapping of filename to contents for each file in the plan
        :rtype:  dict

        :raises tuskar.storage.exceptions.UnknownUUID: if there is no plan
                with the given UUID
        """

        # Load and parse the plan.
        db_plan = self.plan_store.retrieve(plan_uuid)
        master_template = parser.parse_template(
            db_plan.master_template.contents
        )
        environment = parser.parse_environment(
            db_plan.environment_file.contents
        )

        # Compose the plan files and all plan roles and package them into
        # a single dictionary.
        plan_contents = composer.compose_template(master_template)
        env_contents = composer.compose_environment(environment)

        files_dict = {
            'plan.yaml': plan_contents,
            'environment.yaml': env_contents,
        }

        plan_roles = self._find_roles(environment)
        manager = RoleManager()
        for role in plan_roles:
            contents = composer.compose_template(role.template)
            filename = name_utils.role_template_filename(role.name,
                                                         role.version)
            files_dict[filename] = contents

        def _add_template_extra_data_for(templates, template_store):
            template_extra_data=self.template_extra_store.list(
                only_latest=False)
            for template in templates:
                db_template = template_store.retrieve_by_name(template.name)
                template_extra_paths = utils.resolve_template_extra_data(
                    db_template, template_extra_data)
                extra_data_output=manager.template_extra_data_for_output(
                    template_extra_paths)
                files_dict.update(extra_data_output)

        # also grab any extradata files for the role
        _add_template_extra_data_for(plan_roles, self.template_store)

        # in addition to provider roles above, return non-role template files
        reg_mapping = self.registry_mapping_store.list()
        for entry in reg_mapping:
            files_dict[entry.name] = entry.contents

        # similarly, also grab extradata files for the non role templates
        _add_template_extra_data_for(reg_mapping, self.registry_mapping_store)

        return files_dict

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

        reg_mapping = self.registry_mapping_store.list()
        roles = [load_role(e) for e in environment.registry_entries
                 if not any(x.name == e.filename for x in reg_mapping)]
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
