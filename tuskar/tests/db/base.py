# Copyright (c) 2012 NTT DOCOMO, INC.
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

"""Tuskar DB test base class."""

from tuskar.common import context as tuskar_context
from tuskar.tests import base


class DbTestCase(base.TestCase):

    def setUp(self):
        super(DbTestCase, self).setUp()
        self.context = tuskar_context.get_admin_context()

    def create_user_creds(self, ctx, **kwargs):
        ctx_dict = ctx.to_dict()
        ctx_dict.update(kwargs)
        ctx = tuskar_context.RequestContext.from_dict(ctx_dict)
        return self.connection.user_creds_create(ctx)
