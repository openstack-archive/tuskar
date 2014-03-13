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

"""initial migration

Revision ID: 2581ebaf0cb2
Revises: None
Create Date: 2014-03-13 12:14:07.754448

"""

revision = '2581ebaf0cb2'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'overcloud_roles',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=64), unique=True),
        sa.Column('description', sa.String(length=256)),
        sa.Column('image_name', sa.String(length=64)),
        sa.Column('flavor_id', sa.String(length=36)),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.UniqueConstraint('name', name='uniq_overcloud_roles0name'),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    op.create_table(
        'overcloud_role_counts',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('overcloud_role_id', sa.Integer, nullable=False),
        sa.Column('overcloud_id', sa.Integer, nullable=False),
        sa.Column('num_nodes', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.ForeignKeyConstraint(['overcloud_role_id'], ['overcloud_roles.id']),
        sa.ForeignKeyConstraint(['overcloud_id'], ['overclouds.id'], ),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    op.create_table(
        'overclouds',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=64), unique=True),
        sa.Column('description', sa.String(length=256)),
        sa.Column('stack_id', sa.String(length=36)),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.UniqueConstraint('name', name='uniq_overcloud0name'),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )

    op.create_table(
        'overcloud_attributes',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('key', sa.String(length=64), nullable=False),
        sa.Column('value', sa.Text()),
        sa.Column('overcloud_id', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.ForeignKeyConstraint(['overcloud_id'], ['overclouds.id'], ),
        sa.UniqueConstraint('overcloud_id', 'key',
                            name='uniq_overcloud_attributes0overcloud_id0key'),
        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )


def downgrade():
    raise NotImplementedError(('Downgrade from initial migration is'
                               ' unsupported.'))
