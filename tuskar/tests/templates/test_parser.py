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

import datetime
import unittest

from tuskar.templates import heat
from tuskar.templates import parser


TEST_TEMPLATE = """
heat_template_version: 2013-05-23

description: Test provider resource foo

parameters:

  key_name:
    type: string
    description : Name of a KeyPair
    hidden: true
    label: Key

  instance_type:
    type: string
    description: Instance type
    default: m1.small
    constraints:
      - allowed_values: [m1.small, m1.medium, m1.large]
        description: instance_type must be one of m1.small or m1.medium

  image_id:
    type: string
    description: ID of the image to use
    default: 3e6270da-fbf7-4aef-bc78-6d0cfc3ad11b

parameter_groups:

  - label: group-1
    description: first group
    parameters:
      - key_name
      - instance_type

  - label: group-2
    description: second group
    parameters:
      - image_id

resources:
  foo_instance:
    type: OS::Nova::Server
    properties:
      image: { get_param: image_id }
      flavor: { get_param: instance_type }
      key_name: { get_param: key_name }

outputs:
  foo_ip:
    description: IP of the created foo instance
    value: { get_attr: [foo_instance, first_address] }
"""

TEST_ENVIRONMENT = """
parameters:
  key_name: heat_key
  instance_type: m1.small
  image_id: 3e6270da-fbf7-4aef-bc78-6d0cfc3ad11b

resource_registry:
  Tuskar::Foo: provider-foo.yaml
  Tuskar::Bar: provider-bar.yaml
"""


class ParserTests(unittest.TestCase):

    def test_parse_template(self):
        # Test
        t = parser.parse_template(TEST_TEMPLATE)

        # Verify
        self.assertTrue(isinstance(t, heat.Template))
        self.assertEqual(t.version, datetime.date(2013, 5, 23))
        self.assertEqual(t.description, 'Test provider resource foo')

        self.assertEqual(3, len(t.parameters))
        ordered_params = sorted(t.parameters, key=lambda x: x.name)

        # Image ID Parameter
        self.assertEqual('image_id', ordered_params[0].name)
        self.assertEqual('string', ordered_params[0].param_type)
        self.assertEqual('ID of the image to use',
                         ordered_params[0].description)
        self.assertEqual('3e6270da-fbf7-4aef-bc78-6d0cfc3ad11b',
                         ordered_params[0].default)
        self.assertEqual(None, ordered_params[0].hidden)
        self.assertEqual(None, ordered_params[0].label)
        self.assertEqual(0, len(ordered_params[0].constraints))

        # Instance Type Parameter
        self.assertEqual('instance_type', ordered_params[1].name)
        self.assertEqual('string', ordered_params[1].param_type)
        self.assertEqual('Instance type', ordered_params[1].description)
        self.assertEqual('m1.small', ordered_params[1].default)
        self.assertEqual(None, ordered_params[1].hidden)
        self.assertEqual(None, ordered_params[1].label)
        self.assertEqual(1, len(ordered_params[1].constraints))
        c = ordered_params[1].constraints[0]
        self.assertEqual('instance_type must be one of m1.small or m1.medium',
                         c.description)
        self.assertEqual('allowed_values', c.constraint_type)
        self.assertEqual(['m1.small', 'm1.medium', 'm1.large'], c.definition)

        # Key Name Parameter
        self.assertEqual('key_name', ordered_params[2].name)
        self.assertEqual('string', ordered_params[2].param_type)
        self.assertEqual('Name of a KeyPair', ordered_params[2].description)
        self.assertEqual(None, ordered_params[2].default)
        self.assertEqual(True, ordered_params[2].hidden)
        self.assertEqual('Key', ordered_params[2].label)
        self.assertEqual(0, len(ordered_params[2].constraints))

        # Parameter Groups
        self.assertEqual(2, len(t.parameter_groups))
        self.assertEqual('group-1', t.parameter_groups[0].label)
        self.assertEqual('first group',
                         t.parameter_groups[0].description)
        self.assertEqual(sorted(('key_name', 'instance_type')),
                         sorted(t.parameter_groups[0].parameter_names))
        self.assertEqual('group-2', t.parameter_groups[1].label)
        self.assertEqual('second group',
                         t.parameter_groups[1].description)
        self.assertEqual(('image_id',),
                         t.parameter_groups[1].parameter_names)

        # Resources
        self.assertEqual(1, len(t.resources))
        self.assertEqual('foo_instance', t.resources[0].resource_id)
        self.assertEqual('OS::Nova::Server', t.resources[0].resource_type)
        self.assertEqual(3, len(t.resources[0].properties))

        resource_props = sorted(t.resources[0].properties,
                                key=lambda x: x.name)
        self.assertEqual('flavor', resource_props[0].name)
        self.assertEqual({'get_param': 'instance_type'},
                         resource_props[0].value)
        self.assertEqual('image', resource_props[1].name)
        self.assertEqual({'get_param': 'image_id'},
                         resource_props[1].value)
        self.assertEqual('key_name', resource_props[2].name)
        self.assertEqual({'get_param': 'key_name'},
                         resource_props[2].value)

        # Outputs
        self.assertEqual(1, len(t.outputs))
        self.assertEqual('foo_ip', t.outputs[0].name)
        self.assertEqual({'get_attr': ['foo_instance', 'first_address']},
                         t.outputs[0].value)

    def test_parse_environment(self):
        # Test
        e = parser.parse_environment(TEST_ENVIRONMENT)

        # Verify
        self.assertTrue(isinstance(e, heat.Environment))

        # Parameters
        self.assertEqual(3, len(e.parameters))
        ordered_params = sorted(e.parameters, key=lambda x: x.name)
        self.assertEqual('image_id', ordered_params[0].name)
        self.assertEqual('3e6270da-fbf7-4aef-bc78-6d0cfc3ad11b',
                         ordered_params[0].value)
        self.assertEqual('instance_type', ordered_params[1].name)
        self.assertEqual('m1.small', ordered_params[1].value)
        self.assertEqual('key_name', ordered_params[2].name)
        self.assertEqual('heat_key', ordered_params[2].value)

        # Resource Registry
        self.assertEqual(2, len(e.registry_entries))
        ordered_entries = sorted(e.registry_entries, key=lambda x: x.alias)
        self.assertEqual('Tuskar::Bar', ordered_entries[0].alias)
        self.assertEqual('provider-bar.yaml', ordered_entries[0].filename)
        self.assertEqual('Tuskar::Foo', ordered_entries[1].alias)
        self.assertEqual('provider-foo.yaml', ordered_entries[1].filename)
