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
from tempfile import mkdtemp

from tuskar.storage.stores import TemplateStore
from tuskar.storage import template_import
from tuskar.tests.base import TestCase


class TemplateImportTests(TestCase):

    def setUp(self):
        super(TemplateImportTests, self).setUp()
        self.directory = mkdtemp()

        self.store = TemplateStore()

        templates = ['template1.yaml', 'rubbish', 'template2.yaml']
        for template in templates:
            self._create_template(template)

    def _create_template(self, template):
        """Create a mock template file which simple contains it's own name as
        the file contents.
        """
        with open(path.join(self.directory, template), 'w') as f:
            f.write("CONTENTS FOR {0}".format(template))

    def test_list_templates(self):

        # test
        templates = sorted(template_import._list_templates(self.directory))

        # verify
        self.assertEqual([
            ('template1.yaml', path.join(self.directory, "template1.yaml")),
            ('template2.yaml', path.join(self.directory, "template2.yaml")),
        ], templates)

    def test_list_templates_invalid(self):

        # setup
        invalid_path = path.join(self.directory, "FAKEPATH/")
        self.assertFalse(path.isdir(invalid_path))

        # test
        list_call = template_import._list_templates(invalid_path)

        # verify
        self.assertRaises(ValueError, list, list_call)

    def test_dry_run(self):

        # test
        total, created, updated = template_import.importer(
            self.directory, dry_run=True)

        # verify
        self.assertEqual(2, total)
        self.assertEqual([], created)
        self.assertEqual([], updated)

    def test_import(self):

        # test
        total, created, updated = template_import.importer(self.directory)

        # verify
        self.assertEqual(2, total)
        self.assertEqual(['template1.yaml', 'template2.yaml'], sorted(created))
        self.assertEqual([], updated)

    def test_import_update(self):

        # setup
        template_import._create_or_update("template2.yaml", "contents")

        # test
        total, created, updated = template_import.importer(self.directory)

        # verify
        self.assertEqual(2, total)
        self.assertEqual(['template1.yaml', ], created)
        self.assertEqual(['template2.yaml', ], updated)
