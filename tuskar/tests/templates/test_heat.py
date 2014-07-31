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

from tuskar.templates import heat
from tuskar.templates import namespace as ns


class TemplateTests(unittest.TestCase):

    def test_default_version(self):
        self.assertEqual(heat.DEFAULT_VERSION, '2013-05-23')

    def test_init(self):
        # Test
        t = heat.Template(description='test template')
        str(t)  # should not raise an exception

        # Verify
        self.assertEqual(t.version, heat.DEFAULT_VERSION)
        self.assertEqual(t.description, 'test template')
        self.assertEqual(0, len(t.parameters))
        self.assertEqual(0, len(t.parameter_groups))
        self.assertEqual(0, len(t.resources))
        self.assertEqual(0, len(t.outputs))

    def test_add_remove_parameter(self):
        t = heat.Template()
        p = heat.Parameter('test-param', 'test-type')

        # Test Add
        t.add_parameter(p)
        self.assertEqual(1, len(t.parameters))
        self.assertEqual(p, t.parameters[0])

        # Test Remove
        t.remove_parameter(p)
        self.assertEqual(0, len(t.parameters))

    def test_remove_parameters_by_namespace(self):
        # Setup
        t = heat.Template()
        p1 = heat.Parameter(ns.apply_template_namespace('ns1', 'foo'), 't')
        p2 = heat.Parameter(ns.apply_template_namespace('ns2', 'bar'), 't')
        p3 = heat.Parameter(ns.apply_template_namespace('ns1', 'baz'), 't')

        t.add_parameter(p1)
        t.add_parameter(p2)
        t.add_parameter(p3)

        # Test
        t.remove_parameters_by_namespace('ns1')

        # Verify
        self.assertEqual(1, len(t.parameters))
        self.assertEqual(p2, t.parameters[0])

    def test_remove_parameter_not_found(self):
        t = heat.Template()
        self.assertRaises(ValueError, t.remove_parameter,
                          heat.Parameter('n', 't'))

    def test_add_remove_parameter_group(self):
        t = heat.Template()
        pg = heat.ParameterGroup('test-label', 'test-desc')

        # Test Add
        t.add_parameter_group(pg)
        self.assertEqual(1, len(t.parameter_groups))
        self.assertEqual(pg, t.parameter_groups[0])

        # Test Remove
        t.remove_parameter_group(pg)
        self.assertEqual(0, len(t.parameter_groups))

    def test_add_remove_resource(self):
        t = heat.Template()
        r = heat.Resource('id', 't')

        # Test Add
        t.add_resource(r)
        self.assertEqual(1, len(t.resources))
        self.assertEqual(r, t.resources[0])

        # Test Remove
        t.remove_resource(r)
        self.assertEqual(0, len(t.resources))

    def test_remove_resource_by_id(self):
        # Test
        t = heat.Template()
        t.add_resource(heat.Resource('id1', 't1'))
        t.add_resource(heat.Resource('id2', 't2'))

        t.remove_resource_by_id('id1')

        # Verify
        self.assertEqual(1, len(t.resources))
        self.assertEqual(t.resources[0].resource_type, 't2')

    def test_add_remove_output(self):
        t = heat.Template()
        o = heat.Output('n', 'v')

        # Test Add
        t.add_output(o)
        self.assertEqual(1, len(t.outputs))
        self.assertEqual(o, t.outputs[0])

    def test_remove_outputs_by_namespace(self):
        # Setup
        t = heat.Template()

        o1 = heat.Output(ns.apply_template_namespace('ns1', 'foo'), 'v')
        o2 = heat.Output(ns.apply_template_namespace('ns2', 'bar'), 'v')
        o3 = heat.Output(ns.apply_template_namespace('ns1', 'foo'), 'v')

        t.add_output(o1)
        t.add_output(o2)
        t.add_output(o3)

        # Test
        t.remove_outputs_by_namespace('ns1')

        # Verify
        self.assertEqual(1, len(t.outputs))
        self.assertEqual(o2, t.outputs[0])

    def test_remove_output_not_found(self):
        t = heat.Template()
        self.assertRaises(ValueError, t.remove_output, heat.Output('n', 'v'))


class ParameterGroupTests(unittest.TestCase):

    def test_init(self):
        # Test
        g = heat.ParameterGroup('test-label', 'test-desc')
        str(g)  # should not raise an exception

        # Verify
        self.assertEqual(g.label, 'test-label')
        self.assertEqual(g.description, 'test-desc')
        self.assertEqual(0, len(g.parameter_names))

    def test_add_remove_property_name(self):
        g = heat.ParameterGroup('l', 'd')

        # Test Add
        g.add_parameter_name('p1')
        self.assertEqual(1, len(g.parameter_names))
        self.assertEqual('p1', g.parameter_names[0])

        # Test Remove
        g.remove_parameter_name('p1')
        self.assertEqual(0, len(g.parameter_names))

    def test_remove_name_not_found(self):
        g = heat.ParameterGroup('l', 'd')
        g.remove_parameter_name('n1')  # should not error


class ParameterTests(unittest.TestCase):

    def test_init(self):
        # Test
        p = heat.Parameter('test-name', 'test-type', description='test-desc',
                           label='test-label', default='test-default',
                           hidden='test-hidden')
        str(p)  # should not error

        # Verify
        self.assertEqual('test-name', p.name)
        self.assertEqual('test-type', p.param_type)
        self.assertEqual('test-desc', p.description)
        self.assertEqual('test-label', p.label)
        self.assertEqual('test-default', p.default)
        self.assertEqual('test-hidden', p.hidden)

    def test_add_remove_constraint(self):
        p = heat.Parameter('n', 't')
        c = heat.ParameterConstraint('t', 'd')

        # Test Add
        p.add_constraint(c)
        self.assertEqual(1, len(p.constraints))
        self.assertEqual(c, p.constraints[0])

        # Test Remove
        p.remove_constraint(c)
        self.assertEqual(0, len(p.constraints))

    def test_remove_constraint_not_found(self):
        p = heat.Parameter('n', 't')
        self.assertRaises(ValueError, p.remove_constraint,
                          heat.ParameterConstraint('t', 'd'))


class ParameterConstraintTests(unittest.TestCase):

    def test_init(self):
        # Test
        c = heat.ParameterConstraint('test-type', 'test-def',
                                     description='test-desc')
        str(c)  # should not error

        # Verify
        self.assertEqual('test-type', c.constraint_type)
        self.assertEqual('test-def', c.definition)
        self.assertEqual('test-desc', c.description)


class ResourceTests(unittest.TestCase):

    def test_init(self):
        # Test
        r = heat.Resource('test-id',
                          'test-type',
                          metadata='test-meta',
                          depends_on='test-depends',
                          update_policy='test-update',
                          deletion_policy='test-delete')
        str(r)  # should not error

        # Verify
        self.assertEqual('test-id', r.resource_id)
        self.assertEqual('test-type', r.resource_type)
        self.assertEqual('test-meta', r.metadata)
        self.assertEqual('test-depends', r.depends_on)
        self.assertEqual('test-update', r.update_policy)
        self.assertEqual('test-delete', r.deletion_policy)

    def test_add_remove_property(self):
        r = heat.Resource('i', 't')
        p = heat.ResourceProperty('n', 'v')

        # Test Add
        r.add_property(p)
        self.assertEqual(1, len(r.properties))
        self.assertEqual(p, r.properties[0])

        # Test Remove
        r.remove_property(p)
        self.assertEqual(0, len(r.properties))

    def test_remove_property_not_found(self):
        r = heat.Resource('i', 't')
        self.assertRaises(ValueError, r.remove_property,
                          heat.ResourceProperty('n', 'v'))


class ResourcePropertyTests(unittest.TestCase):

    def test_init(self):
        # Test
        p = heat.ResourceProperty('test-name', 'test-value')
        str(p)  # should not error

        # Verify
        self.assertEqual('test-name', p.name)
        self.assertEqual('test-value', p.value)


class OutputTests(unittest.TestCase):

    def test_init(self):
        # Test
        o = heat.Output('test-name', 'test-value', description='test-desc')
        str(o)  # should not error

        # Verify
        self.assertEqual('test-name', o.name)
        self.assertEqual('test-value', o.value)
        self.assertEqual('test-desc', o.description)


class EnvironmentTests(unittest.TestCase):

    def test_init(self):
        # Test
        e = heat.Environment()
        str(e)  # should not error

    def test_add_remove_parameter(self):
        e = heat.Environment()
        p = heat.EnvironmentParameter('n', 'v')

        # Test Add
        e.add_parameter(p)
        self.assertEqual(1, len(e.parameters))
        self.assertEqual(p, e.parameters[0])

        # Test Remove
        e.remove_parameter(p)
        self.assertEqual(0, len(e.parameters))

    def test_remove_parameter_not_found(self):
        e = heat.Environment()
        self.assertRaises(ValueError, e.remove_parameter,
                          heat.EnvironmentParameter('n', 'v'))

    def test_remove_parameters_by_namespace(self):
        # Setup
        e = heat.Environment()

        p1 = heat.EnvironmentParameter(
            ns.apply_template_namespace('ns1', 'n1'), 'v')
        p2 = heat.EnvironmentParameter(
            ns.apply_template_namespace('ns2', 'n2'), 'v')
        p3 = heat.EnvironmentParameter(
            ns.apply_template_namespace('ns1', 'n3'), 'v')

        e.add_parameter(p1)
        e.add_parameter(p2)
        e.add_parameter(p3)

        # Test
        e.remove_parameters_by_namespace('ns1')

        # Verify
        self.assertEqual(1, len(e.parameters))
        self.assertEqual(p2, e.parameters[0])

    def test_add_remove_registry_entry(self):
        e = heat.Environment()
        re = heat.RegistryEntry('a', 'f')

        # Test Add
        e.add_registry_entry(re)
        self.assertEqual(1, len(e.registry_entries))
        self.assertEqual(re, e.registry_entries[0])

        # Test Remove
        e.remove_registry_entry(re)
        self.assertEqual(0, len(e.registry_entries))

    def test_remove_registry_entry_not_found(self):
        e = heat.Environment()
        self.assertRaises(ValueError, e.remove_registry_entry,
                          heat.RegistryEntry('a', 'f'))

    def test_remove_registry_entry_by_namespace(self):
        # Setup
        e = heat.Environment()

        e.add_registry_entry(heat.RegistryEntry('a1', 'f1'))
        e.add_registry_entry(heat.RegistryEntry('a2', 'f2'))
        e.add_registry_entry(heat.RegistryEntry('a1', 'f3'))

        # Test
        e.remove_registry_entry_by_alias('a1')

        # Verify
        self.assertEqual(1, len(e.registry_entries))
        self.assertEqual(e.registry_entries[0].filename, 'f2')

    def test_find_parameter_by_name(self):
        # Setup
        e = heat.Environment()
        parameter = heat.EnvironmentParameter('p1', 'v1')
        e.add_parameter(parameter)

        # Test
        found = e.find_parameter_by_name('p1')

        # Verify
        self.assertTrue(found is parameter)

    def test_find_parameter_by_name_missing_parameter(self):
        # Setup
        e = heat.Environment()

        # Test
        self.assertRaises(ValueError, e.find_parameter_by_name, 'missing')


class EnvironmentParameterTests(unittest.TestCase):

    def test_init(self):
        # Test
        p = heat.EnvironmentParameter('test-name', 'test-value')
        str(p)  # should not error

        # Verify
        self.assertEqual('test-name', p.name)
        self.assertEqual('test-value', p.value)


class ModuleMethodTests(unittest.TestCase):

    def test_safe_strip(self):
        self.assertEqual('foo', heat._safe_strip('  foo   '))
        self.assertEqual(None, heat._safe_strip(None))
