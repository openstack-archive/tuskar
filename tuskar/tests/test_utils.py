# Copyright 2011 Justin Santa Barbara
# Copyright 2012 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tuskar.common import utils
from tuskar.storage import models
from tuskar.tests import base


class CommonUtilsTestCase(base.TestCase):

    def test_resolve_role_extra_name_from_path(self):
        expected = [{"/path/to/FOO": "extra_FOO_"},
                    {"/hieradata/config.yaml": "extra_config_yaml"},
                    {"./name.has.dots": "extra_name.has_dots"},
                    {"/path/name.": "extra_name_"},
                    {"/path/cdefile.c": "extra_cdefile_c"}, ]

        for params in expected:
            path = params.keys()[0]
            res = utils.resolve_role_extra_name_from_path(path)
            self.assertEqual(params[path], res)

    def test_resolve_template_file_name_from_role_extra_name(self):
        expected = [{"extra_FOO_": "FOO"},
                    {"extra_config_yaml": "config.yaml"},
                    {"extra_name.has_dots": "name.has.dots"},
                    {"extra_name_": "name"}, ]
        for params in expected:
            name = params.keys()[0]
            res = utils.resolve_template_file_name_from_role_extra_name(name)
            self.assertEqual(params[name], res)

    def test_resolve_template_extra_data(self):
        template_contents = """ Foo Bar Baz
                                    get_file: foo/bar.baz
                            """
        template_extra = models.StoredFile(
            uuid="1234", contents="boo!", store=None, name="extra_bar_baz")
        template = models.StoredFile(
            uuid="1234", contents=template_contents, store=None)
        res = utils.resolve_template_extra_data(template, [template_extra])
        self.assertEqual(res, [{"extra_bar_baz": "foo/bar.baz"}])


class IntLikeTestCase(base.TestCase):

    def test_is_int_like(self):
        self.assertTrue(utils.is_int_like(1))
        self.assertTrue(utils.is_int_like("1"))
        self.assertTrue(utils.is_int_like("514"))
        self.assertTrue(utils.is_int_like("0"))

        self.assertFalse(utils.is_int_like(1.1))
        self.assertFalse(utils.is_int_like("1.1"))
        self.assertFalse(utils.is_int_like("1.1.1"))
        self.assertFalse(utils.is_int_like(None))
        self.assertFalse(utils.is_int_like("0."))
        self.assertFalse(utils.is_int_like("aaaaaa"))
        self.assertFalse(utils.is_int_like("...."))
        self.assertFalse(utils.is_int_like("1g"))
        self.assertFalse(
            utils.is_int_like("0cc3346e-9fef-4445-abe6-5d2b2690ec64"))
        self.assertFalse(utils.is_int_like("a1"))
