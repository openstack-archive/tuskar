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

from mock import call
from mock import patch

from tuskar.cmd import delete_roles
from tuskar.tests.base import TestCase


class DeleteRoleTests(TestCase):

    CMD = """ tuskar-delete-roles --dryrun """
    UUIDS = """ 3 4 5 """

    @patch('tuskar.storage.stores.TemplateStore.retrieve', return_value="boo")
    @patch('tuskar.cmd.delete_roles._print_names')
    def test_main(self, mock_print, mock_read):
        main_args = "%s --uuids %s" % (self.CMD, self.UUIDS)
        expected_res = ['3', '4', '5', 'No deletions, dryrun']
        # test
        delete_roles.main(argv=(main_args).split())

        # verify
        self.assertEqual([call('Deleted', expected_res)],
                         mock_print.call_args_list)
