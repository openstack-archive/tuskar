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
import time
import yaml

from tripleo_heat_merge import merge as tht_merge
from tuskar.common import exception as exc

CONF = cfg.CONF
template_path = CONF.tht_local_dir
compute_path = os.path.abspath(os.path.join(template_path,
                                "nova-compute-instance.yaml"))
controller_path = os.path.abspath(os.path.join(template_path,
                                "notcompute.yaml"))
object_path = os.path.abspath(os.path.join(template_path,
                                "swift-source.yaml"))
block_path = os.path.abspath(os.path.join(template_path,
                                "block-storage.yaml"))

#TODO(marios):work out how to include swift here... talk to Derek Higins
#see I4a70ffbf9c51f1fea5cfc84d8718d3d30d36b3f2
RCS = {'compute': {'name': 'NovaCompute',
                   'template': compute_path,
                    'subkey': 'Resources.NovaCompute0'
                  },
        'controller': {'name': 'notcompute',
                       'template': controller_path,
                        'subkey': 'Resources.notcompute'
                      },
        'object': {'name': 'swiftTBD',
                    'template': object_path,
                    'subkey': 'TBD'
                  },
        'block': {'name': 'BlockStorage',
                    'template': block_path,
                    'subkey': 'Resources.BlockStorage0'
                  },
      }


def _add_instance_blocks(count, type, rs):
    for i in range(count):
        node_name = "%s%s" % (RCS[type]['name'], i)
        rs['Resources'][node_name] = {}
        rs['Resources'][node_name]['Type'] = 'FileInclude'
        rs['Resources'][node_name]['Path'] = RCS[type]['template']
        rs['Resources'][node_name]['Subkey'] = RCS[type]['subkey']
        rs['Resources'][node_name]['Parameters'] = {}
        #TODO(marios): work out params for each type and pass them
        #here, e.g. override the template NovaImage for compute:
        #rs['Resources'][node_name]['Parameters']['NovaImage'] = 'fooimg'


#TODO(marios): need to work out how to handle the flavors/aggregates
#the current mako templates are not being used here

#Look at review: /#/c/66062/. No more ResourceClasses...expecting sthing like:
# {
#     'resource_categories': { 'controller': 1, 'compute': 4, 'object': 1,
#                              'block': 2}
# }
#
def generate_template(rcs):
    rs = {'Resources': {}}
    #build up template for merging:
    for rc, count in rcs['resource_categories'].items():
        rc = rc.lower()
        if rc in RCS:
            _add_instance_blocks(count, rc, rs)
        else:
            raise exc.InvalidResourceCategory(rc)
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
                                  os.path.abspath(temp_file_name)], None, None,
                                  included_template_dir=template_path)
    return template
