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

from tuskar.templates import namespace


class NamespaceTests(unittest.TestCase):

    def test_apply_template_namespace(self):
        namespaced = namespace.apply_template_namespace('test-ns', 'test-name')
        self.assertEqual(namespaced, 'test-ns::test-name')
        self.assertTrue(namespace.matches_template_namespace('test-ns',
                                                             namespaced))

    def test_remove_template_namespace(self):
        stripped = namespace.remove_template_namespace('test-ns::test-name')
        self.assertEqual(stripped, 'test-name')

    def test_matches_template_namespace(self):
        value = 'test-ns::test-name'
        self.assertTrue(namespace.matches_template_namespace('test-ns', value))
        self.assertFalse(namespace.matches_template_namespace('fake', value))

    def test_apply_resource_alias_namespace(self):
        namespaced = namespace.apply_resource_alias_namespace('compute')
        self.assertEqual(namespaced, 'Tuskar::compute')

    def test_remove_resource_alias_namespace(self):
        stripped = namespace.remove_resource_alias_namespace(
            'Tuskar::controller')
        self.assertEqual(stripped, 'controller')
