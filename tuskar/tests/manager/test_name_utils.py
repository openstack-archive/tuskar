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

import unittest

from tuskar.manager import name_utils


class NameUtilsTestCases(unittest.TestCase):

    def test_generate_role_namespace(self):
        ns = name_utils.generate_role_namespace('r1', 'v1')
        self.assertEqual('r1-v1', ns)

    def test_parse_role_namespace(self):
        name, version = name_utils.parse_role_namespace('r1-v1')
        self.assertEqual('r1', name)
        self.assertEqual('v1', version)

    def test_parse_role_namespace_multiple_dash(self):
        name, version = name_utils.parse_role_namespace('all-in-one-v1')
        self.assertEqual('all-in-one', name)
        self.assertEqual('v1', version)

    def test_role_template_filename(self):
        filename = name_utils.role_template_filename('r1', 'v1', None)
        self.assertEqual('provider-r1-v1.yaml', filename)

    def test_role_template_filename_with_relative_path(self):
        filename = name_utils.role_template_filename('r1', 'v1', 'l1')
        self.assertEqual('l1/provider-r1-v1.yaml', filename)

    def test_master_template_filename(self):
        filename = name_utils.master_template_filename('p1')
        self.assertEqual('p1-template.yaml', filename)

    def test_environment_filename(self):
        filename = name_utils.environment_filename('p1')
        self.assertEqual('p1-environment.yaml', filename)
