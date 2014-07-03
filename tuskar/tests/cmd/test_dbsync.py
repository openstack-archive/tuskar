#!/usr/bin/env python
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
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

from mock import patch

from tuskar.cmd.dbsync import main
from tuskar.tests.base import TestCase


class DBSyncCommandTests(TestCase):

    @patch('tuskar.db.migration.db_sync')
    def test_main(self, mock_db_sync):

        try:
            main(['test.py', '--config-file', 'etc/tuskar/tuskar.conf.sample'])

            # Catch BaseException's and re-raise as Exception, otherwise
            # exceptions raised by the argument parser code wont be caught and
            # create a cryptic test failure.
        except BaseException as e:
            raise Exception(e)

        mock_db_sync.assert_called_once_with()
