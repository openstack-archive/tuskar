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

from mock import call
from mock import patch

from tuskar.cmd import load_roles
from tuskar.tests.base import TestCase


class LoadRoleTests(TestCase):

    @patch('tuskar.storage.load_roles._list_roles',
           return_value=[['role_name.yaml', '/path/role_name.yaml']])
    @patch('tuskar.storage.load_roles._load_file', return_value="YAML")
    @patch('tuskar.cmd.load_roles._print_names')
    def test_main(self, mock_print, mock_read, mock_list):

        # test
        load_roles.main(argv="--master-seed=seed.yaml path".split())

        # verify
        self.assertEqual([
            call('Created', ['role_name.yaml'])
        ], mock_print.call_args_list)
