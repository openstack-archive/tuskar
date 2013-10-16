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
""" Util for using merge.py to generate overcloud.yaml to hand over to Heat. Translates Tuskar resources into the overcloud heat template, using merge.py from upstream tripleo-heat-templates """

import time
import os
import subprocess
import yaml

def generate_template(rcs):
    import pdb;pdb.set_trace()
    tuskar_resources = {'Resources' : {}}
    for rc in rcs:
        for rack in rc.racks:
            for node in rack.nodes:
                node_name  = 'NovaCompute%s' % (node.id)
                tuskar_resources['Resources'][node_name] = {}
                tuskar_resources['Resources'][node_name]['Type']= 'FileInclude'
                tuskar_resources['Resources'][node_name]['Path']= 'nova-compute-instance.yaml'
                tuskar_resources['Resources'][node_name]['Subkey']= 'Resources.NovaCompute0'
                tuskar_resources['Resources'][node_name]['Parameters']= {}
                tuskar_resources['Resources'][node_name]['Parameters']['AvailabilityZone'] = 'nova::%s' % node.id
    pdb.set_trace()
    file_name = 'tuskar_resource_%s.yaml' % int(round(time.time()))
    path = '%s/../api/templates/tripleo-heat-templates/%s'  %(os.path.dirname(__file__), file_name)
    tuskar_resource_file = open(path, 'w+')
    tuskar_resource_file.write(yaml.dump(tuskar_resources, default_flow_style=False))
    return tuskar_resource_file

#merge with overcloud.yaml using merge.py. see tripleo-heat-templates
def merge_templates(temp_file):
    # YEAH... SRSLY FIX THIS FIRST
    subprocess.call("cd ./tuskar/api/templates/tripleo-heat-templates ; python merge.py overcloud-source.yaml " +
                    os.path.abspath(temp_file.name) + "> overcloud.yaml" , shell=True)

    pass
    #call merge.py
