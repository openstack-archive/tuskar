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

from datetime import datetime
from functools import partial

from mock import Mock

from tuskar.storage.exceptions import NameAlreadyUsed
from tuskar.storage.exceptions import UnknownUUID
from tuskar.storage.models import StoredFile
from tuskar.storage import stores
from tuskar.tests.base import TestCase


class BaseStoreTests(TestCase):

    def setUp(self):
        super(BaseStoreTests, self).setUp()

        self.driver = Mock()
        self.store = stores._BaseStore(self.driver)

    def test_create(self):
        self.store.create("My contents")
        self.driver.create.assert_called_once_with(
            self.store, None, "My contents")

    def test_update(self):
        uuid = "d131dd02c5e6eec4"
        contents = "Stored contents"
        self.store.update(uuid, contents)
        self.driver.update.assert_called_once_with(self.store, uuid, contents)

    def test_retrieve(self):
        uuid = "d131dd02c5e6eec5"
        self.store.retrieve(uuid)
        self.driver.retrieve.assert_called_once_with(self.store, uuid)

    def test_delete(self):
        uuid = "d131dd02c5e6eec6"
        self.store.delete(uuid)
        self.driver.delete.assert_called_once_with(self.store, uuid)

    def test_list(self):
        self.store.list()
        self.driver.list.assert_called_once_with(self.store)


class NamedStoreTests(TestCase):

    def setUp(self):
        super(NamedStoreTests, self).setUp()

        self.driver = Mock()
        self.store = stores._NamedStore(self.driver)

    def test_create(self):
        name = "Object name"
        self.store.create(name, "My contents")
        self.driver.create.assert_called_once_with(
            self.store, name, "My contents")

    def test_update(self):
        uuid = "d131dd02c5e6eec4"
        contents = "Stored contents"
        self.store.update(uuid, contents)
        self.driver.update.assert_called_once_with(self.store, uuid, contents)

    def test_retrieve(self):
        uuid = "d131dd02c5e6eec5"
        self.store.retrieve(uuid)
        self.driver.retrieve.assert_called_once_with(self.store, uuid)

    def test_delete(self):
        uuid = "d131dd02c5e6eec6"
        self.store.delete(uuid)
        self.driver.delete.assert_called_once_with(self.store, uuid)

    def test_list(self):
        self.store.list()
        self.driver.list.assert_called_once_with(self.store)

    def test_retrieve_by_name(self):
        name = "Object name"
        self.store.retrieve_by_name(name)
        self.driver.retrieve_by_name.assert_called_once_with(self.store, name)


class VersionedStoreTests(TestCase):

    def setUp(self):
        super(VersionedStoreTests, self).setUp()

        self.driver = Mock()
        self.store = stores._VersionedStore(self.driver)

    def test_create(self):
        name = "Object name"
        self.store.create(name, "My contents")
        self.driver.create.assert_called_once_with(
            self.store, name, "My contents")

    def test_update(self):
        uuid = "d131dd02c5e6eec4"
        contents = "Stored contents"
        self.store.update(uuid, contents)
        self.driver.update.assert_called_once_with(self.store, uuid, contents)

    def test_retrieve(self):
        uuid = "d131dd02c5e6eec5"
        self.store.retrieve(uuid)
        self.driver.retrieve.assert_called_once_with(self.store, uuid)

    def test_delete(self):
        uuid = "d131dd02c5e6eec6"
        self.store.delete(uuid)
        self.driver.delete.assert_called_once_with(self.store, uuid)

    def test_list(self):
        self.store.list()
        self.driver.list.assert_called_once_with(self.store, only_latest=False)

        self.driver.list.reset_mock()

        self.store.list(only_latest=True)
        self.driver.list.assert_called_once_with(self.store, only_latest=True)

    def test_retrieve_by_name(self):
        name = "Object name"
        version = 1
        self.store.retrieve_by_name(name, version)
        self.driver.retrieve_by_name.assert_called_once_with(
            self.store, name, version)


class TemplateStoreTests(TestCase):

    def setUp(self):
        super(TemplateStoreTests, self).setUp()

        self.driver = Mock()
        self.store = stores.TemplateStore(self.driver)

    def test_create(self):
        name = "template name"
        contents = "template contents"
        self.store.create(name, contents)
        self.driver.create.assert_called_once_with(self.store, name, contents)


class EnvironmentFileTests(TestCase):

    def setUp(self):
        super(EnvironmentFileTests, self).setUp()

        self.driver = Mock()
        self.store = stores.EnvironmentFileStore(self.driver)

    def test_create(self):
        contents = "environment contents"
        self.store.create(contents)
        self.driver.create.assert_called_once_with(self.store, None, contents)


class DeploymentPlanMockedTests(TestCase):

    def setUp(self):
        super(DeploymentPlanMockedTests, self).setUp()

        self.driver = Mock()

        self.master_template_store = Mock()
        self.environment_store = Mock()

        self.store = stores.DeploymentPlanStore(
            driver=self.driver,
            master_template_store=self.master_template_store,
            environment_store=self.environment_store
        )

    def _stored_file(self, name, contents):

        dt = datetime.now()

        return StoredFile(
            uuid="Plan UUID",
            contents=contents,
            store="deployment_plan",
            name=name,
            created_at=dt,
            updated_at=None,
            version=1,
        )

    def _create_mock_plan(self):

        contents = ('{"environment_file_uuid": "Environment UUID", '
                    '"master_template_uuid": "Template UUID"}')
        self.driver.retrieve.return_value = Mock(
            uuid="Plan UUID",
            contents=contents
        )
        self.master_template_store.retrieve.return_value = Mock(
            uuid="Template UUID"
        )
        self.environment_store.retrieve.return_value = Mock(
            uuid="Environment UUID"
        )

    def test_create(self):

        name = "deployment_plan name"
        contents = ('{"environment_file_uuid": "Environment UUID", '
                    '"master_template_uuid": "Template UUID"}')

        self.driver.create.return_value = self._stored_file(name, contents)

        result = self.store.create(name, 'Template UUID', 'Environment UUID')
        self.driver.create.assert_called_once_with(self.store, name, contents)

        self.assertEqual(result.name, name)

        self.master_template_store.retrieve.assert_called_once_with(
            'Template UUID')
        self.environment_store.retrieve.assert_called_once_with(
            'Environment UUID')

    def test_create_no_template(self):

        name = "deployment_plan name"
        contents = ('{"environment_file_uuid": "Environment UUID", '
                    '"master_template_uuid": "UUID1"}')

        self.driver.create.return_value = self._stored_file(name, contents)
        self.master_template_store.create.return_value = Mock(uuid="UUID1")

        result = self.store.create(name, environment_uuid='Environment UUID')

        self.master_template_store.create.assert_called_once_with(
            'deployment_plan name', '')
        self.assertItemsEqual(self.environment_store.create.call_args_list, [])

        self.driver.create.assert_called_once_with(self.store, name, contents)

        self.assertEqual(result.name, name)
        self.master_template_store.retrieve.assert_called_once_with('UUID1')
        self.environment_store.retrieve.assert_called_once_with(
            'Environment UUID')

    def test_create_no_environment(self):

        name = "deployment_plan name"
        contents = ('{"environment_file_uuid": "UUID2", '
                    '"master_template_uuid": "Template UUID"}')

        self.driver.create.return_value = self._stored_file(name, contents)
        self.environment_store.create.return_value = Mock(uuid="UUID2")

        result = self.store.create(name, master_template_uuid='Template UUID')

        self.environment_store.create.assert_called_once_with('')
        self.assertItemsEqual(
            self.master_template_store.create.call_args_list, [])

        self.driver.create.assert_called_once_with(self.store, name, contents)

        self.assertEqual(result.name, name)
        self.master_template_store.retrieve.assert_called_once_with(
            'Template UUID')
        self.environment_store.retrieve.assert_called_once_with(
            'UUID2')

    def test_retrieve(self):

        # setup
        self._create_mock_plan()

        # test
        retrieved = self.store.retrieve("Plan UUID")

        # verify
        self.assertEqual("Plan UUID", retrieved.uuid)
        self.assertEqual("Template UUID", retrieved.master_template.uuid)
        self.assertEqual("Environment UUID", retrieved.environment_file.uuid)

    def test_update_nothing(self):

        # setup
        self._create_mock_plan()

        # setup
        update_call = partial(self.store.update, "Plan UUID")

        # test & verify
        self.assertRaises(ValueError, update_call)
        self.assertItemsEqual(self.driver.update.call_args_list, [])


class DeploymentPlanTests(TestCase):

    def setUp(self):
        super(DeploymentPlanTests, self).setUp()

        self.master_template_store = stores.MasterTemplateStore()
        self.environment_store = stores.EnvironmentFileStore()
        self.store = stores.DeploymentPlanStore(
            master_template_store=self.master_template_store,
            environment_store=self.environment_store
        )

        self._create_plan()

    def _create_plan(self):

        contents = "Template Contents"
        self.template = self.master_template_store.create("Template", contents)
        self.env = self.environment_store.create("Environment Contents")

        self.plan = self.store.create(
            "Plan Name", self.template.uuid, self.env.uuid)

    def test_create(self):

        name = "deployment_plan name"

        result = self.store.create(name, self.template.uuid, self.env.uuid)

        self.assertEqual(result.name, name)

    def test_create_duplicate(self):

        # setup
        name = "deployment_plan name"
        self.store.create(name, self.template.uuid, self.env.uuid)
        create_call = partial(self.store.create, name)

        # test & verify
        self.assertRaises(NameAlreadyUsed, create_call)

    def test_create_no_template(self):

        name = "deployment_plan name"
        result = self.store.create(name, environment_uuid=self.env.uuid)
        self.assertEqual(result.name, name)

    def test_create_no_environment(self):

        name = "deployment_plan name"
        template_uuid = self.template.uuid
        result = self.store.create(name, master_template_uuid=template_uuid)
        self.assertEqual(result.name, name)

    def test_retrieve(self):

        # test
        retrieved = self.store.retrieve(self.plan.uuid)

        # verify
        self.assertEqual(self.plan.uuid, retrieved.uuid)
        self.assertEqual(self.template.uuid, retrieved.master_template.uuid)
        self.assertEqual(self.env.uuid, retrieved.environment_file.uuid)

    def test_update_template_manual(self):

        # setup
        plan = self.store.create("plan")

        new_template = self.store._template_store.update(
            plan.master_template.uuid, "NEW CONTENT")

        # test
        updated = self.store.update(
            plan.uuid, master_template_uuid=new_template.uuid)

        # verify
        retrieved = self.store.retrieve(plan.uuid)
        self.assertEqual(plan.uuid, retrieved.uuid)
        self.assertEqual(updated.master_template.uuid, new_template.uuid)

    def test_update_environment_manual(self):

        # setup
        plan = self.store.create("plan")

        new_env = self.store._env_file_store.update(
            plan.environment_file.uuid, "NEW CONTENT")

        # test
        updated = self.store.update(
            plan.uuid, environment_uuid=new_env.uuid)

        # verify
        retrieved = self.store.retrieve(plan.uuid)
        self.assertEqual(plan.uuid, retrieved.uuid)
        self.assertEqual(updated.environment_file.uuid, new_env.uuid)

    def test_update_nothing(self):

        # setup
        update_call = partial(self.store.update, self.plan.uuid)

        # test & verify
        self.assertRaises(ValueError, update_call)

    def test_update_master_template(self):

        # setup
        new_contents = "New Template Contents."
        self.assertEqual("Template Contents", self.template.contents)

        # test
        updated = self.store.update_master_template(
            self.plan.uuid, new_contents)

        # verify
        updated_template = updated.master_template
        updated_env = updated.environment_file

        self.assertEqual(self.plan.uuid, updated.uuid)
        self.assertEqual(self.plan.master_template.uuid, updated_template.uuid)
        self.assertEqual(self.plan.environment_file.uuid, updated_env.uuid)

        self.assertEqual(updated.master_template.contents, new_contents)
        self.assertEqual(updated.environment_file.contents, self.env.contents)

    def test_update_environment(self):

        # setup
        new_contents = "New Environment Contents."
        self.assertEqual("Environment Contents", self.env.contents)

        # test
        updated = self.store.update_environment(
            self.plan.uuid, new_contents)

        # verify
        updated_template = updated.master_template
        updated_env = updated.environment_file

        self.assertEqual(self.plan.uuid, updated.uuid)
        self.assertEqual(self.plan.master_template.uuid, updated_template.uuid)
        self.assertEqual(self.plan.environment_file.uuid, updated_env.uuid)

        self.assertEqual(
            updated.master_template.contents, self.template.contents)
        self.assertEqual(updated.environment_file.contents, new_contents)

    def test_list(self):

        plans = self.store.list()

        self.assertEqual(1, len(plans))

        plan, = plans

        self.assertEqual(plan.uuid, self.plan.uuid)

    def test_retrieve_by_name(self):

        plan = self.store.retrieve_by_name("Plan Name")

        self.assertEqual(plan.uuid, self.plan.uuid)

    def test_delete(self):

        # test
        self.store.delete(self.plan.uuid)

        # verify
        plan_retrieve = partial(self.store.retrieve, self.plan.uuid)
        template_retrieve = partial(self.master_template_store.retrieve,
                                    self.template.uuid)
        env_retrieve = partial(self.environment_store.retrieve, self.env.uuid)

        for call in [plan_retrieve, template_retrieve, env_retrieve]:
            self.assertRaises(UnknownUUID, call)

    def test_delete_no_template(self):

        # setup
        self.master_template_store.delete(self.template.uuid)

        # test
        self.store.delete(self.plan.uuid)

        # verify
        plan_retrieve = partial(self.store.retrieve, self.plan.uuid)
        template_retrieve = partial(self.master_template_store.retrieve,
                                    self.template.uuid)
        env_retrieve = partial(self.environment_store.retrieve, self.env.uuid)

        for call in [plan_retrieve, template_retrieve, env_retrieve]:
            self.assertRaises(UnknownUUID, call)

    def test_delete_no_environment(self):

        # setup
        self.environment_store.delete(self.env.uuid)

        # test
        self.store.delete(self.plan.uuid)

        # verify
        plan_retrieve = partial(self.store.retrieve, self.plan.uuid)
        template_retrieve = partial(self.master_template_store.retrieve,
                                    self.template.uuid)
        env_retrieve = partial(self.environment_store.retrieve, self.env.uuid)

        for call in [plan_retrieve, template_retrieve, env_retrieve]:
            self.assertRaises(UnknownUUID, call)
