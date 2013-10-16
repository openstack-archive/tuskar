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

import mock
import unittest

from tuskar.heat import template_tools


URL_OVERCLOUDS = '/v1/overclouds'


class TemplateToolsTests(unittest.TestCase):
    @mock.patch('tripleo_heat_merge.merge.parse_scaling',
                return_value={'NovaCompute0': 12})
    def test_generate_scaling_params(self, mock_scaling):
        # Setup
        rcs = {'overcloud_roles': {'controller': 1, 'compute': 12},
               'fake': 'fun'}

        # Test
        result = template_tools.generate_scaling_params(rcs)

        # Verify
        self.assertEqual(result, {'NovaCompute0': 12})

    @mock.patch('tripleo_heat_merge.merge.parse_scaling',
                return_value={'NovaCompute0': 12})
    @mock.patch('tripleo_heat_merge.merge.merge',
                return_value='template')
    def test_merge_templates(self, mock_merge, mock_scaling):
        # Setup
        rcs = {'overcloud_roles': {'controller': 1, 'compute': 12},
               'fake': 'fun'}

        # Test
        result = template_tools.merge_templates(rcs)

        # Verify
        self.assertEqual(result, 'template')
