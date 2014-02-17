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


class TemplateToolsTests(unittest.TestCase):

    @mock.patch('tripleo_heat_merge.merge.parse_scaling')
    def test_generate_scaling_params(self, mock_parse_scaling):
        # Setup
        overcloud_roles = {'controller': 1, 'overcloud-compute': 12}

        # Test
        template_tools.generate_scaling_params(overcloud_roles)

        # Verify
        mock_parse_scaling.assert_called_once_with(['NovaCompute=12'])

    @mock.patch('tripleo_heat_merge.merge.merge')
    def test_merge_templates(self, mock_merge):
        # Setup
        overcloud_roles = {'controller': 1, 'overcloud-compute': 12}

        # Test
        template_tools.merge_templates(overcloud_roles)

        # Verify
        mock_merge.assert_called_once_with([
            '/etc/tuskar/tripleo-heat-templates/overcloud-source.yaml',
            '/etc/tuskar/tripleo-heat-templates/ssl-source.yaml',
            '/etc/tuskar/tripleo-heat-templates/swift-source.yaml'],
            None,
            None,
            scaling={
                'NovaCompute0': 12
            },
            included_template_dir='/etc/tuskar/tripleo-heat-templates/'
        )
