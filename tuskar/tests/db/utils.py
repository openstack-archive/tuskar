# Copyright (c) 2013 Red Hat
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

import uuid

import sqlalchemy
from tuskar.api.controllers.v1.types.capacity import Capacity
from tuskar.api.controllers.v1.types.flavor import Flavor
from tuskar.api.controllers.v1.types.link import Link
from tuskar.api.controllers.v1.types.node import Node
from tuskar.api.controllers.v1.types.rack import Rack
from tuskar.api.controllers.v1.types.relation import Relation
from tuskar.api.controllers.v1.types.resource_class import ResourceClass
from tuskar.openstack.common.db.sqlalchemy import session as db_session


def get_test_resource_class(**kwargs):
    rc = ResourceClass(
        name=kwargs.get('name', 'test_resource_class'),
        service_type=kwargs.get('type', 'compute'),
        image_id=kwargs.get('image_id', 'f1852b4a-1ae8-4e36-8d45-2d72e2f12ba4')
    )
    return rc


def get_test_flavor(**kwargs):
    flavor = Flavor(name=kwargs.get('name', 'one'),
                    capacities=[
                        Capacity(name='cpu',
                                 value=kwargs.get('value', '1'),
                                 unit='count'),
                        Capacity(name='memory',
                                 value=kwargs.get('value', '1'),
                                 unit='MiB'),
                        Capacity(name='storage',
                                 value=kwargs.get('value', '1'),
                                 unit='GiB')])
    return flavor


def get_test_rack(**kwargs):
    rack = Rack(subnet=kwargs.get('subnet', '192.168.1.0/24'),
                slots=kwargs.get('slots', 1),
                name=kwargs.get('name', 'my_rack'),
                capacities=[
                    Capacity(name='total_cpu',
                             value=kwargs.get('total_cpu', '64'),
                             unit='count'),
                    Capacity(name='total_memory',
                             value=kwargs.get('total_memory', '8192'),
                             unit='MiB')],
                nodes=[])
    if kwargs.get('nodes', False):
        rack.nodes = [Node(id=str(uuid.uuid4())), Node(id=str(uuid.uuid4()))]
    if kwargs.get('resource_class', False):
        rack.resource_class = Relation(
            id=kwargs.get('rc_id', 1),
            links=[Link(href='http://0.0.0.0:8585/resource_classes/' +
                        str(kwargs.get('rc_id', 1)), rel='self')])
    return rack


def get_test_rack_node(**kwargs):
    node = Node(id=kwargs.get('id', '1'))
    return node
    rack = Rack(subnet=kwargs.get('subnet', '192.168.1.0/255'),
                slots=kwargs.get('slots', 1),
                name=kwargs.get('name', 'my_rack'),
                capacities=[
                    Capacity(name='total_cpu',
                             value=kwargs.get('total_cpu', '64'),
                             unit='count'),
                    Capacity(name='total_memory',
                             value=kwargs.get('total_memory', '8192'),
                             unit='MiB')],
                nodes=[
                    Node(id='123'),
                    Node(id='345')])
    return rack


def get_test_resource_class_rack(**kwargs):
    rack_id = kwargs.get('id', 1)
    rc_rack = Relation(id=rack_id,
                       links=[Link(href='http://0.0.0.0:8585/v1/racks/' +
                                   str(rack_id), rel='self')])
    return rc_rack


def get_db_table(table_name):
    metadata = sqlalchemy.MetaData()
    metadata.bind = db_session.get_engine()
    return sqlalchemy.Table(table_name, metadata, autoload=True)
