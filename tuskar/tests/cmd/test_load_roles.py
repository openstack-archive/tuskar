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
from tuskar.cmd import load_seed
from tuskar.tests.base import TestCase


class LoadRoleTests(TestCase):

    ROLES = """ -r role_name1.yaml -r /path/role_name2.yaml
                --role /path1/role_name3.yaml """

    ROLE_EXTRA = """ --role-extra /path/metadata/compute_data.yaml
                     -re /path/metadata/common_data.yaml """

    ENV_DATA = """
resource_registry:
  OS::TripleO::Another: required_file.yaml
    """

    @patch('tuskar.storage.load_utils.load_file', return_value="YAML")
    @patch('tuskar.cmd.load_roles._print_names')
    def test_main(self, mock_print, mock_read):
        main_args = " --master-seed=seed.yaml %s %s" % (
            self.ROLES, self.ROLE_EXTRA)
        expected_res = ['role_name1', 'role_name2', 'role_name3',
                        'extra_compute_data_yaml', 'extra_common_data_yaml']

        # test
        load_roles.main(argv=(main_args).split())

        # verify
        self.assertEqual([call('Created', expected_res)],
                         mock_print.call_args_list)

    def test_load_seed_invalid_args(self):
        main_args = "tuskar-load-seed"
        self.assertRaises(SystemExit, load_seed.main, main_args.split())

        main_args = "tuskar-load-seed --master-seed=seed.yaml"
        self.assertRaises(SystemExit, load_seed.main, main_args.split())

        main_args = "tuskar-load-seed --resource-registry=registry.yaml"
        self.assertRaises(SystemExit, load_seed.main, main_args.split())

    @patch('tuskar.storage.load_utils.load_file', return_value="YAML")
    @patch('tuskar.storage.load_roles.load_file', return_value=ENV_DATA)
    @patch('tuskar.cmd.load_seed._print_names')
    def test_load_seed(self, mock_print, mock_read, mock_read2):
        main_args = ("tuskar-load-seed --master-seed=seed.yaml"
                     " --resource-registry=registry.yaml")
        expected_created = ['_master_seed', '_registry', 'required_file.yaml']

        load_seed.main(argv=(main_args).split())

        self.assertEqual([call('Created', expected_created)],
                         mock_print.call_args_list)
