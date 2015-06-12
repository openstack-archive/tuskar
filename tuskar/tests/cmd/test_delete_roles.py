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

from mock import patch

from tuskar.cmd import delete_roles
from tuskar.tests.base import TestCase


class DeleteRoleTests(TestCase):

    @patch('tuskar.storage.delete_roles.delete_roles')
    def test_main_single_uuid(self, mock_delete):
        # Setup
        cmd = """ tuskar-delete-roles --uuid foo """

        # Test
        delete_roles.main(argv=(cmd.split()))

        # Verify
        mock_delete.assert_called_once_with(['foo'], noop=False)

    @patch('tuskar.storage.delete_roles.delete_roles')
    def test_main_multiple_uuids(self, mock_delete):
        # Setup
        cmd = """ tuskar-delete-roles --uuid foo --uuid bar """

        # Test
        delete_roles.main(argv=(cmd.split()))

        # Verify
        mock_delete.assert_called_once_with(['foo', 'bar'], noop=False)

    @patch('tuskar.storage.delete_roles.delete_all_roles')
    def test_main_all(self, mock_delete):
        # Setup
        cmd = """ tuskar-delete-roles --all """

        # Test
        delete_roles.main(argv=(cmd.split()))

        # Verify
        mock_delete.assert_called_once_with(noop=False)

    @patch('tuskar.storage.delete_roles.delete_all_roles')
    def test_main_all_dryrun(self, mock_delete):
        # Setup
        cmd = """ tuskar-delete-roles --all --dryrun """

        # Test
        delete_roles.main(argv=(cmd.split()))

        # Verify
        mock_delete.assert_called_once_with(noop=True)

    @patch('tuskar.storage.delete_roles.delete_roles')
    def test_main_uuid_dryrun(self, mock_delete):
        # Setup
        cmd = """ tuskar-delete-roles --uuid foo --dryrun """

        # Test
        delete_roles.main(argv=(cmd.split()))

        # Verify
        mock_delete.assert_called_once_with(['foo'], noop=True)

    @patch('tuskar.storage.delete_roles.delete_roles')
    def test_main_no_roles(self, mock_delete):
        # Setup
        cmd = """ tuskar-delete-roles """

        # Test
        self.assertRaises(SystemExit, delete_roles.main, argv=(cmd.split()))
