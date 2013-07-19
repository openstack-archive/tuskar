# vim: tabstop=4 shiftwidth=4 softtabstop=4
# -*- encoding: utf-8 -*-
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""SQLAlchemy storage backend."""

from oslo.config import cfg

# TODO(deva): import MultipleResultsFound and handle it appropriately
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import subqueryload, joinedload

from tuskar.common import exception
from tuskar.db import api
from tuskar.db.sqlalchemy import models
from tuskar.openstack.common.db.sqlalchemy import session as db_session
from tuskar.openstack.common import log
from wsme import types as wtypes

CONF = cfg.CONF
CONF.import_opt('connection',
                'tuskar.openstack.common.db.sqlalchemy.session',
                group='database')

LOG = log.getLogger(__name__)

get_engine = db_session.get_engine
get_session = db_session.get_session


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


class Connection(api.Connection):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    def get_heat_data(self):
        session = get_session()
        result = session.query(models.ResourceClass).options(
                    joinedload(models.ResourceClass.racks),
                ).all()
        # FIXME: This idio*ic pre-caching must happen here otherwise you get
        # this error when rendering the template:
        #
        # Parent instance <Rack at 0x2abd5d0> is not bound to a Session; lazy load
        # operation of attribute 'nodes' cannot proceed
        #
        for resource_class in result:
            for rack in resource_class.racks:
                for node in rack.nodes:
                    session.query(models.Rack).options(
                            subqueryload('capacities'),
                            subqueryload('nodes')
                            ).get(rack.id)
        session.close()
        return result

    def get_racks(self, columns):
        session = get_session()
        result = session.query(models.Rack).options(
                    subqueryload('capacities'),
                    subqueryload('nodes')
                ).all()
        session.close()
        return result

    def get_rack(self, rack_id):
        session = get_session()
        try:
            result = session.query(models.Rack).options(
                    subqueryload('capacities'),
                    subqueryload('nodes')
                    ).filter_by(id=rack_id).one()
        except NoResultFound:
            raise exception.RackNotFound(rack=rack_id)

        return result

    def get_racks_by_resource_class(self, resource_class_id):
        session = get_session()
        return session.query(models.Rack
                            ).filter_by(resource_class_id=resource_class_id
                            ).all()

    def get_resource_classes(self, columns):
        session = get_session()
        resource_classes = session.query(models.ResourceClass).all()
        session.close()
        return resource_classes

    def get_resource_class(self, resource_class_id):
        session = get_session()
        try:
            result = session.query(models.ResourceClass
                                ).filter_by(id=resource_class_id).one()
        except NoResultFound:
            raise exception.ResourceClassNotFound(
                    resource_class=resource_class_id
                    )
        session.close()
        return result

    def create_resource_class(self, new_resource_class):
        session = get_session()
        session.begin()
        try:
            rc = models.ResourceClass(name=new_resource_class.name,
            service_type=new_resource_class.service_type)
            session.add(rc)
            if new_resource_class.racks:
                for r in new_resource_class.racks:
                    # FIXME surely there is a better way of doing this.
                    rack = self.get_rack(r.get_id())
                    session.add(rack)
                    rack.resource_class = rc
            if new_resource_class.flavors:
                for flav in new_resource_class.flavors:
                    flavor = self.create_flavor(flav)
                    session.add(flavor)
                    flavor.resource_class = rc
        except Exception:
            session.rollback()
            raise

        session.commit()
        session.refresh(rc)
        session.close()
        return rc

    def update_resource_class(self, resource_class_id, new_resource_class):
        rc = self.get_resource_class(resource_class_id)

        session = get_session()
        session.begin()
        try:
            if new_resource_class.name:
                rc.name = new_resource_class.name

            if new_resource_class.service_type:
                rc.service_type = new_resource_class.service_type

            session.add(rc)

            if not isinstance(new_resource_class.racks, wtypes.UnsetType):
                rc.racks = []
                for r in new_resource_class.racks:
                    rack = self.get_rack(r.get_id())
                    session.add(rack)
                    rc.racks.append(rack)

        except Exception:
            session.rollback()
            raise

        session.commit()
        session.refresh(rc)
        session.close()
        return rc

    #creates a new flavor and adds it to the specified resource_clas
    #returns the new Flavor
    def create_resource_class_flavor(self, resource_class_id, new_flavor):

        rc = self.get_resource_class(resource_class_id)
        session = get_session()
        session.begin()
        try:
            flavor = self.create_flavor(new_flavor)
            session.add(flavor)
            flavor.resource_class = rc
            rc.flavors.append(flavor)
        except Exception:
            session.rollback()
            raise

        session.commit()
        session.refresh(rc)
        session.close()
        return flavor

    def update_resource_class_flavor(self, resource_class_id, flavor_id, new_flavor):
        session = get_session()
        session.begin()
        try:
            flavor  = self.get_flavor(flavor_id)

            if new_flavor.name:
                flavor.name = new_flavor.name

            session.add(flavor)

            for new_c in new_flavor.capacities:
                #need index here for removal
                for i in range(len(flavor.capacities)):
                    old_c = flavor.capacities[i]
                    if old_c.name == new_c.name:
                        new_capacity = models.Capacity(name=new_c.name, value=new_c.value, unit=new_c.unit)
                        flavor.capacities.remove(old_c)
                        flavor.capacities.append(new_capacity)
                        session.delete(old_c)
                        session.add(new_capacity)
                        session.add(flavor)

            session.commit()
            session.refresh(flavor)
            return flavor
        except Exception:
            session.rollback()
            raise

    def update_rack(self, rack_id, new_rack):
        session = get_session()
        session.begin()
        try:
            rack = self.get_rack(rack_id)

            # FIXME(mfojtik): The update below is a bit retar*ed,
            # There must be a better way how to do 'update' in sqlalchemy.
            #
            if new_rack.name:
                rack.name = new_rack.name

            if new_rack.slots:
                rack.slots = new_rack.slots

            if new_rack.subnet:
                rack.subnet = new_rack.subnet

            if new_rack.chassis:
                rack.chassis_id = new_rack.chassis.id

            if not isinstance(new_rack.resource_class, wtypes.UnsetType):
                rc = self.get_resource_class(new_rack.resource_class.get_id())
                rack.resource_class_id = rc.id
                session.add(rc)

            if new_rack.location:
                rack.location = new_rack.location

            session.add(rack)

            # TODO(mfojtik): Since the 'PUT' does not behave like PATCH, we
            # need to replace all capacities, even if you want to add/update a
            # value of single item
            #
            if not isinstance(new_rack.capacities, wtypes.UnsetType):
                [session.delete(c) for c in rack.capacities]

                for c in new_rack.capacities:
                    capacity = models.Capacity(name=c.name, value=c.value)
                    session.add(capacity)
                    rack.capacities.append(capacity)
                    session.add(rack)

            if not isinstance(new_rack.nodes, wtypes.UnsetType):
                [session.delete(n) for n in rack.nodes]

                for n in new_rack.nodes:
                    node = models.Node(node_id=n.id)
                    session.add(node)
                    rack.nodes.append(node)
                    session.add(rack)

            session.commit()
            session.refresh(rack)
            return rack
        except Exception:
            session.rollback()
            raise

    def create_rack(self, new_rack):
        session = get_session()
        session.begin()
        try:
            # FIXME: So actually these two are *mandatory* attributes:
            #
            rack = models.Rack(
                     name=new_rack.name,
                     subnet=new_rack.subnet,
                   )

            # FIXME: And there are 'optional':
            #
            if new_rack.location:
                rack.location = new_rack.location

            if new_rack.slots:
                rack.slots = new_rack.slots

            if not isinstance(new_rack.resource_class, wtypes.UnsetType):
                rc = self.get_resource_class(new_rack.resource_class.get_id())
                rack.resource_class_id = rc.id
                session.add(rc)

            session.add(rack)

            if new_rack.capacities:
                for c in new_rack.capacities:
                    capacity = models.Capacity(name=c.name, value=c.value)
                    session.add(capacity)
                    rack.capacities.append(capacity)
                    session.add(rack)

            if new_rack.nodes:
                for n in new_rack.nodes:
                    node = models.Node(node_id=n.id)
                    session.add(node)
                    rack.nodes.append(node)
                    session.add(rack)

            session.commit()
            session.refresh(rack)
            return rack
        except Exception as e:
            session.rollback()
            raise e

    def delete_rack(self, rack_id):
        session = get_session()
        rack = self.get_rack(rack_id)
        session.begin()
        try:
            session.delete(rack)
            [session.delete(c) for c in rack.capacities]
            [session.delete(n) for n in rack.nodes]
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise

    def delete_resource_class(self, resource_class_id):
        session = get_session()
        session.begin()
        try:
            # FIXME (mtaylor) we should also set the foreign key to None for
            # all associated Racks
            session.query(models.ResourceClass
                          ).filter_by(id=resource_class_id).delete()
            session.commit()
        except Exception:
            session.rollback()
            raise

    def get_flavors(self, resource_class_id):
        session = get_session()
        return session.query(models.Flavor).filter_by(
                resource_class_id=resource_class_id
                )

    def get_flavor(self, flavor_id):
        session = get_session()
        try:
            flavor = session.query(models.Flavor).options(
                    subqueryload('capacities'),
                    ).filter_by(id=flavor_id).one()
        except NoResultFound:
            raise exception.FlavorNotFound(flavor=flavor_id)
        return flavor

    def create_flavor(self, new_flavor):
        session = get_session()
        #CALL NOVA AT THIS POINT (code in tuskar/compute/nova.py)
        #NOT YET TESTED - FIXME
        with session.begin():
            flavor = models.Flavor(name=new_flavor.name)
            session.add(flavor)
            for c in new_flavor.capacities:
                capacity = models.Capacity(name=c.name,
                                           value=c.value,
                                           unit=c.unit)
                session.add(capacity)
                flavor.capacities.append(capacity)
                session.add(flavor)
            return flavor

    def delete_flavor(self, flavor_id):
        session = get_session()
        flavor = self.get_flavor(flavor_id)
        with session.begin():
            if self.delete_capacities(flavor, session):
                session.delete(flavor)
                return True

    def delete_capacities(self, resource, session):
        try:
            for c in resource.capacities:
                session.delete(c)
        except Exception:
            session.rollback()
            return False
        return True
