# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2013 Red Hat                # All Rights Reserved.

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

#
import simpleyaml

from novaclient import exceptions as NovaClientExceptions
from novaclient.v1_1 import client
from oslo.config import cfg
from tuskar.db.sqlalchemy import api as db_api

#from tuskar.common import exception
#from tuskar.openstack.common import jsonutils
from tuskar.openstack.common import log

nova_opts = [
    cfg.StrOpt('nova_undercloud_config',
               default='etc/tuskar/nova_undercloud_config.yml',
               help='nova undercloud keystone uri and credentials'),
]

LOG = log.getLogger(__name__)
CONF = cfg.CONF
CONF.register_opts(nova_opts)


#lame little mock class - REMOVE ME AT YOUR EARLIEST CONVENIENCE
#useful when you want to run Tuskar but not actually call to Nova
#for creation of undercloud flavs/aggs... just set call_nova: "False"
#in etc/tuskar/nova_undercloud_config.yml
class LameMockClient(object):

    class MockClientObj(object):
        id = "1234567890"

        def __getattr__(self, name):
            def _missing(*args, **kwargs):
                return self
            return _missing

    def __getattr__(self, name):
        return self.MockClientObj()


class NovaClient(object):

    def __init__(self):
        #grab client params from nova_undercloud_config.yml:
        try:
            config_file = open(CONF.nova_undercloud_config)
            client_params = simpleyaml.safe_load(config_file)
            config_file.close()
        except Exception:
            raise
        if client_params['call_nova'] == "True":
            self.nova_client = client.Client(client_params['nova_username'],
                                             client_params['nova_password'],
                                             client_params['nova_tenantname'],
                                             client_params['keystone_url'],
                                             service_type="compute")
        else:
            self.nova_client = LameMockClient()

    #takes a resource class (DB model) as input,called from controller
    #registers HostAggregate and Flavor, with all metadata
    #returns [aggregate_id, flavor_id] for storing in database
    #also adds any rack nodes into the aggregate
    def register_resource_class_aggregate_flavor(self, resource_class):
        #e.g. o_cloud_compute_m1, o_cloud_storage_s2 etc
        name = 'o_cloud_' + resource_class.service_type + \
            '_' + resource_class.name
        #aggregate
        aggregate_id = self.create_host_aggregate(name)
        self.set_host_aggregate_metadata(aggregate_id, name)
        #flavor - assumption: values of flavor attributes here are of
        #no consequence... just the metadata... so set everythin to '1'
        flavor_id = self.create_flavor(None, name, vcpus=1, memory=1, disk=1)
        self.set_flavor_metadata(flavor_id, name)
        #now add any hosts in resource_class.racks.nodes into the created
        #host aggregate so the scheduling will work
        racks = db_api.Connection.get_racks_by_resource_class(
            db_api.get_backend(),
            resource_class.id)
        for rack in racks:
            for node in rack.nodes:
                self.add_node_to_aggregate(aggregate_id, node.node_id)
        return aggregate_id, flavor_id

    def unregister_resource_class_aggregate_flavors(self, resource_class):
        #delete flavors:
        if resource_class.flavor_id:
            self.delete_flavor(resource_class.flavor_id)
        #remove nodes from aggregate:
        #FIXME: do we need to do this? or can we just delete the aggregate?
        if resource_class.host_aggregate_id:
            racks = db_api.Connection.get_racks_by_resource_class(
                db_api.get_backend(),
                resource_class.id)
            for rack in racks:
                for node in rack.nodes:
                    self.remove_node_from_aggregate(
                        resource_class.host_aggregate_id,
                        node.node_id)
            #delete the aggregate:
            self.delete_host_aggregate(resource_class.host_aggregate_id)
        return True

    #def update_host_aggregate_nodes(self, resource_class):
    #    #remove/clear all previous nodes/hosts in the aggregate...
    #    for rack in resource_class.racks:
    #        for node in rack.nodes:
    #            self.remove_node_from_aggregate(
    #                resource_class.host_aggregate_id,
    #                node.node_id)
    #    #add all the nodes in parameter resource_class to the aggregate:
    #    for rack in resource_class.racks:
    #        for node in rack.nodes

    def get_flavors(self):
        """Calls out to Nova for a list of detailed flavor information."""
        try:
            flavors = self.nova_client.flavors.list()
        except Exception:
            raise
        #should convert response to some local Flavor object - controller/db?
        #TODO() ^^^ FIXME - right now we aren't using this method
        return flavors

    #returns newly created flavor uuid from nova
    def create_flavor(self, flavor_data, flav_name, **kwargs):
        try:
            if kwargs.get('vcpus'):
                cpu = kwargs.get('vcpus')
                ram = kwargs.get('memory')
                disk = kwargs.get('disk')
            else:
                ram, cpu, disk, ephemeral, swap = \
                    self.extract_from_capacities(flavor_data)
            nova_flavor = self.nova_client.flavors.create(
                flav_name, ram, cpu, disk)
            return nova_flavor.id
        except Exception as e:
            if ("Instance Type with name %s already exists" % (flav_name,)) \
                    in e.message:
                for flav in self.get_flavors():
                    if flav.name == flav_name:
                        return flav.id
            else:
                raise

    def set_flavor_metadata(self, flavor_id, class_name):
        try:
            flav = self.nova_client.flavors.get(flavor_id)
            flav.set_keys({'class': class_name})
        except Exception as e:
            raise
        return flav

    def delete_flavor(self, nova_flavor_id):
        try:
            self.nova_client.flavors.delete(nova_flavor_id)
        except Exception as e:
            if ("%s could not be found" % (nova_flavor_id)) in e.message:
                return True
            else:
                raise
        return True

    def get_host_aggregates(self):
        try:
            aggs = self.nova_client.aggregates.list()
        except Exception:
            raise
        return aggs

    #create a host aggregate for a resource class, use rc name
    def create_host_aggregate(self, name):
        try:
            #the None here is for the required availability_zone param:
            agg = self.nova_client.aggregates.create(name, None)
        except NovaClientExceptions.Conflict:
            #could be that aggregate already exists, if so update metadata:
            found = False
            for aggregate in self.get_host_aggregates():
                if name == aggregate.name:
                    return aggregate.id
            #if we haven't found it, doesn't already exist, raise the error
            raise
        except Exception:
            raise
        return agg.id

    #add a host (node) to a host aggregate:
    def add_node_to_aggregate(self, aggregate_id, node_id):
        try:
            self.nova_client.aggregates.add_host(aggregate_id, node_id)
        except Exception:
            raise
        return True

    #remove host (node) from aggregate
    def remove_node_from_agregate(self, aggregate_id, node_id):
        try:
            self.nova_client.aggregates.remove_host(aggregate_id, node_id)
        except Exception:
            raise
        return True

    #set host aggregate metadata
    def set_host_aggregate_metadata(self, host_aggregate_id, class_name):
        try:
            agg = self.nova_client.aggregates.set_metadata(
                host_aggregate_id,
                {'class': class_name})
        except Exception as e:
            raise
        return agg

    def delete_host_aggregate(self, aggregate_id):
        try:
            self.nova_client.aggregates.delete(aggregate_id)
        except NovaClientExceptions.NotFound:
            return True
        except Exception as e:
            raise
        return True

    def extract_from_capacities(self, flavor_data):
        ram = cpu = root_disk = ephemeral = swap = 0
        for c in flavor_data.capacities:
            if c.name in ["memory", "ram"]:
                ram = c.value
            elif c.name in ["cpu", "vcpu"]:
                cpu = c.value
            elif c.name in ["storage", "root_disk"]:
                root_disk = c.value
            elif c.name in ["ephemeral_disk", "ephemeral"]:
                ephemeral = c.value
            elif c.name in ["swap", "swap_disk"]:
                swap = c.value
        return ram, cpu, root_disk, ephemeral, swap
