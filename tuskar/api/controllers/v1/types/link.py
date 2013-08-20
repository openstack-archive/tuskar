# vim: tabstop=4 shiftwidth=4 softtabstop=4
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
from oslo.config import cfg

#import wsme
from wsme import types as wtypes

from tuskar.api.controllers.v1.types.base import Base

CONF = cfg.CONF

ironic_opts = [
    cfg.StrOpt('ironic_url',
               default='http://ironic.local:6543/v1',
               help='Ironic API entrypoint URL'),
]

CONF.register_opts(ironic_opts)


class Link(Base):
    """A link representation."""

    href = wtypes.text
    "The url of a link."

    rel = wtypes.text
    "The name of a link."

    @classmethod
    def build(self, rel_name, url, type, type_arg):
        return Link(href=('%s/v1/%s/%s') % (url, type, type_arg), rel=rel_name)

    @classmethod
    def build_ironic_link(self, rel_name, resource_id):
        return Link(href=('%s/%s') % (CONF.ironic_url, resource_id),
                    rel=rel_name)
