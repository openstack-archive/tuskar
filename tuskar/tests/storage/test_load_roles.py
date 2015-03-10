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

from os import path
from shutil import rmtree
from tempfile import mkdtemp

from tuskar.storage import load_roles
from tuskar.storage import stores
from tuskar.tests.base import TestCase


class LoadRoleTests(TestCase):

    def setUp(self):
        super(LoadRoleTests, self).setUp()
        self.directory = mkdtemp()

        self.store = stores.TemplateStore()

        roles_name = ['role1.yaml', 'role2.yml']
        self.roles = [path.join(self.directory, role) for role in roles_name]

        for role in self.roles:
            self._create_file(role)

    def tearDown(self):
        super(LoadRoleTests, self).tearDown()
        rmtree(self.directory)

    def _create_file(self, file, data=None):
        """Create a mock file which contains its own name as the file
        contents when the data argument is empty.
        """

        if data is None:
            data = "CONTENTS FOR {0}".format(file)

        with open(file, 'w') as f:
            f.write(data)

    def test_import(self):

        # test
        total, created, updated = load_roles.load_roles(self.roles)

        # verify
        self.assertEqual(['role1', 'role2'], sorted(total))
        self.assertEqual(['role1', 'role2'], sorted(created))
        self.assertEqual([], updated)

    def test_import_update(self):

        # setup
        load_roles._create_or_update("role2", "contents")

        # test
        total, created, updated = load_roles.load_roles(self.roles)

        # verify
        self.assertEqual(['role1', 'role2'], sorted(total))
        self.assertEqual(['role1', ], created)
        self.assertEqual(['role2', ], updated)

    def test_import_with_seed(self):
        # Setup
        self._create_file(path.join(self.directory, 'seed'))

        # Test
        seed_file = path.join(self.directory, 'seed')
        total, created, updated = load_roles.load_roles(self.roles,
                                                        seed_file=seed_file)

        # Verify
        self.assertEqual(['_master_seed', 'role1', 'role2'], sorted(total))
        self.assertEqual(['_master_seed', 'role1', 'role2'], sorted(created))
        self.assertEqual([], updated)

    def test_import_seed_and_registry(self):
        env_data = """
resource_registry:
  OS::TripleO::Role: role1.yaml
  OS::TripleO::Another: required_file.yaml
        """

        # Setup
        self._create_file(path.join(self.directory, 'seed'))
        self._create_file(path.join(self.directory, 'environment'), env_data)
        self._create_file(path.join(self.directory, 'required_file.yaml'))

        # Test
        seed_file = path.join(self.directory, 'seed')
        env_file = path.join(self.directory, 'environment')
        all_roles, created, updated = load_roles.load_roles(
            self.roles,
            seed_file=seed_file,
            resource_registry_path=env_file)

        # Verify
        self.assertEqual(['_master_seed', '_registry',
                          'role1', 'role2'], sorted(all_roles))
        self.assertEqual(['_master_seed', '_registry', 'required_file.yaml',
                          'role1', 'role2'], sorted(created))
        self.assertEqual([], updated)
