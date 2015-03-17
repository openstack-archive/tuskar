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

from oslo.db.sqlalchemy import utils
from sqlalchemy import Column, String


def upgrade(migrate_engine):
    stored_file = utils.get_table(migrate_engine, 'stored_file')
    relative_path = Column('relative_path', String(256), nullable=True)
    stored_file.create_column(relative_path)


def downgrade(migrate_engine):
    raise NotImplementedError('Downgrade is unsupported.')
