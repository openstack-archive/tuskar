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

from tuskar.storage.load_templates import _create_or_update
from tuskar.storage.load_templates import _list_templates
from tuskar.storage.load_templates import load_templates
from tuskar.storage.stores import TemplateStore
from tuskar.tests.base import TestCase


class LoadTemplateTests(TestCase):

    def setUp(self):
        super(LoadTemplateTests, self).setUp()
        self.directory = mkdtemp()

        self.store = TemplateStore()

        templates = ['template1.yaml', 'rubbish', 'template2.yml']
        for template in templates:
            self._create_template(template)

    def tearDown(self):
        super(LoadTemplateTests, self).tearDown()
        rmtree(self.directory)

    def _create_template(self, template):
        """Create a mock template file which simple contains it's own name as
        the file contents.
        """
        with open(path.join(self.directory, template), 'w') as f:
            f.write("CONTENTS FOR {0}".format(template))

    def test_list_templates(self):

        # test
        templates = sorted(_list_templates(self.directory))

        # verify
        self.assertEqual([
            ('template1.yaml', path.join(self.directory, "template1.yaml")),
            ('template2.yml', path.join(self.directory, "template2.yml")),
        ], templates)

    def test_list_templates_invalid(self):

        # setup
        invalid_path = path.join(self.directory, "FAKEPATH/")
        self.assertFalse(path.isdir(invalid_path))

        # test
        list_call = _list_templates(invalid_path)

        # verify
        self.assertRaises(ValueError, list, list_call)

    def test_dry_run(self):

        # test
        total, created, updated = load_templates(
            self.directory, dry_run=True)

        # verify
        self.assertEqual(['template1.yaml', 'template2.yml'], sorted(total))
        self.assertEqual([], created)
        self.assertEqual([], updated)

    def test_import(self):

        # test
        total, created, updated = load_templates(self.directory)

        # verify
        self.assertEqual(['template1.yaml', 'template2.yml'], sorted(total))
        self.assertEqual(['template1.yaml', 'template2.yml'], sorted(created))
        self.assertEqual([], updated)

    def test_import_update(self):

        # setup
        _create_or_update("template2.yml", "contents")

        # test
        total, created, updated = load_templates(self.directory)

        # verify
        self.assertEqual(['template1.yaml', 'template2.yml'], sorted(total))
        self.assertEqual(['template1.yaml', ], created)
        self.assertEqual(['template2.yml', ], updated)
