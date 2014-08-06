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
from tuskar.tests import base


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
