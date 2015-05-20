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

from oslo_db.sqlalchemy import utils
from sqlalchemy import MetaData

from tuskar.db.sqlalchemy.types import LongText
from tuskar.openstack.common.gettextutils import _  # noqa
from tuskar.openstack.common import log as logging


LOG = logging.getLogger(__name__)

ENGINE = 'InnoDB'
CHARSET = 'utf8'


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    stored_file = utils.get_table(migrate_engine, 'stored_file')

    try:
        LOG.info(repr(stored_file))
        col = stored_file._columns.get('contents')
        col.alter(type=LongText)
    except Exception:
        LOG.info(repr(stored_file))
        LOG.exception(_('Exception while creating table.'))
        raise


def downgrade(migrate_engine):
    raise NotImplementedError('Downgrade is unsupported.')
