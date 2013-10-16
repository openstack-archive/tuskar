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
""" Util for using merge.py to generate overcloud.yaml to hand over to Heat.
    Translates Tuskar resources into the overcloud heat template, using
    merge.py from upstream tripleo-heat-templates """

import os
from oslo.config import cfg
import sys
import time
import yaml
#FIXME(marios): tripleo_heat_merge not pip findable yet
sys.path.append('/usr/lib/python2.7/site-packages/')
from tripleo_heat_merge import merge as tht_merge

CONF = cfg.CONF
template_path = CONF.tht_local_dir

#TODO(marios): need to work out how to handle the flavors/aggregates
#the current mako templates are not being used here


def generate_template(rcs):
    rs = {'Resources': {}}
    for rc in rcs:
        for rack in rc.racks:
            for node in rack.nodes:
                if rc.service_type == "compute":
                    node_name = 'NovaCompute%s' % (node.id)
                    rs['Resources'][node_name] = {}
                    rs['Resources'][node_name]['Type'] = 'FileInclude'
                    rs['Resources'][node_name]['Path'] = os.path.abspath(
                      os.path.join(template_path, "nova-compute-instance.yaml")
                      )
                    rs['Resources'][node_name]['Subkey'] = \
                                                    'Resources.NovaCompute0'
                elif rc.service_type == "controller":
                    node_name = 'notcompute'
                    rs['Resources'][node_name] = {}
                    rs['Resources'][node_name]['Type'] = 'FileInclude'
                    rs['Resources'][node_name]['Path'] = os.path.abspath(
                            os.path.join(template_path, "notcompute.yaml"))
                    rs['Resources'][node_name]['Subkey'] = \
                                                    'Resources.notcompute'
                rs['Resources'][node_name]['Parameters'] = {}
                rs['Resources'][node_name]['Parameters']['AvailabilityZone'] =\
                                                    'nova::%s' % node.id
    file_name = 'tuskar_resource_%s.yaml' % int(round(time.time()))
    path = os.path.join(template_path, file_name)
    tuskar_resource_file = open(path, 'w+')
    tuskar_resource_file.write(yaml.dump(rs, default_flow_style=False))
    tuskar_resource_file.close()
    #return the path
    return tuskar_resource_file.name


#merge with overcloud.yaml using merge.py. see tripleo-heat-templates
def merge_templates(temp_file_name):
    template = tht_merge.merge([os.path.abspath(os.path.join(os.path.dirname(
                                  temp_file_name), "overcloud-source.yaml")),
                                          os.path.abspath(temp_file_name)])
    return template
