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
            self._create_role(role)

    def tearDown(self):
        super(LoadRoleTests, self).tearDown()
        rmtree(self.directory)

    def _create_role(self, role):
        """Create a mock role file which simple contains it's own name as
        the file contents.
        """

        with open(role, 'w') as f:
            f.write("CONTENTS FOR {0}".format(role))

    def test_dry_run(self):

        # test
        total, created, updated = load_roles.load_roles(
            self.roles, dry_run=True)

        # verify
        self.assertEqual(['role1', 'role2'], sorted(total))
        self.assertEqual([], created)
        self.assertEqual([], updated)

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
        self._create_role(path.join(self.directory, 'seed'))

        # Test
        seed_file = path.join(self.directory, 'seed')
        total, created, updated = load_roles.load_roles(self.roles,
                                                        seed_file=seed_file)

        # Verify
        self.assertEqual(['_master_seed', 'role1', 'role2'], sorted(total))
        self.assertEqual(['_master_seed', 'role1', 'role2'], sorted(created))
        self.assertEqual([], updated)
