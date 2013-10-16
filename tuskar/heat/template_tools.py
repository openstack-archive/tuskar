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
import time
import yaml

from oslo.config import cfg
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

COMPUTE_CONFIG = ''


#TODO(marios):work out how to include swift here... talk to Derek Higins
#see I4a70ffbf9c51f1fea5cfc84d8718d3d30d36b3f2
RCS = {'compute': {'name': 'NovaCompute',
                   'template': compute_path,
                   'subkey': 'Resources.NovaCompute0',
                   'image_param': 'NovaImage',
                   'base_count': 1
                  },
       'controller': {'name': 'notcompute',
                      'template': controller_path,
                       'subkey': 'Resources.notcompute',
                       'image_param': 'notcomputeImage',
                       'base_count': 1
                      },
       'object': {'name': 'swiftTBD',
                  'template': object_path,
                  'subkey': 'TBD',
                  'image_param': 'TBD',
                  'base_count': 0
                  },
       'block': {'name': 'BlockStorage',
                 'template': block_path,
                 'subkey': 'Resources.BlockStorage0',
                 'image_param': 'BlockStorageImage',
                 'base_count': 0
                  },
      }


def _get_image_id(db_categories, cat_name):
    for cat in db_categories:
        if cat.name == cat_name:
            return cat.image_id
    #TODO(marios): in theory we would have validated that all the user
    #requested categories are in the database categories... so should be
    #no need to raise error here if image_id not found. VERIFY THIS


def _add_instance_blocks(count, rc_name, rs, db_categories):
    if count == 1 and (rc_name in ['compute', 'controller']):
        #already have NovaCompute0 and notcompute from overcloud-source.yaml
        return
    else:
        for i in xrange(RCS[rc_name]['base_count'], count):
            #starting at NovaCompute1 for example
            node_name = "%s%s" % (RCS[rc_name]['name'], i)
            rs['Resources'][node_name] = {}
            rs['Resources'][node_name]['Type'] = 'FileInclude'
            rs['Resources'][node_name]['Path'] = RCS[rc_name]['template']
            rs['Resources'][node_name]['SubKey'] = RCS[rc_name]['subkey']
            rs['Resources'][node_name]['Parameters'] = {}
            #TODO(marios): work out any other params for each type of
            #resource category and pass them here, for now just image_id
            #TODO(marios): comment out the retrieval of image_id until the
            #controllers are ready (so we can populate the database):
            #
            # rs['Resources'][node_name]['Parameters'][RCS[rc_name]['image_param']]
            #        = _get_image_id(db_categories, rc_name)


#TODO(marios): need to work out how to handle the flavors/aggregates
#the current mako templates are not being used here

#Look at review: /#/c/66062/. No more ResourceClasses...expecting sthing like:
# {
#     'resource_categories': { 'controller': 1, 'compute': 4, 'object': 1,
#                              'block': 2}
# }
#
def generate_template(rcs, db_categories):
    rs = {'Resources': {}}
    #TODO(marios): validate that what we get from the database for categories
    #matches what the user sent in the request...
    #category_names = []
    #for cat in db_categories:
    #    category_names.append(cat.name)
    #build up template for merging:
    for rc, count in rcs['resource_categories'].items():
        rc = rc.lower()
        if rc in RCS:
            _add_instance_blocks(count, rc, rs, db_categories)
        else:
            raise exc.InvalidResourceCategory(rc)
    file_name = 'tuskar_resource_%s.yaml' % int(round(time.time()))
    path = os.path.join(template_path, file_name)
    with open(path, 'w+') as tuskar_resource_file:
        tuskar_resource_file.write(yaml.dump(rs, default_flow_style=False))
    tuskar_resource_file.close()
    """return the path"""
    return tuskar_resource_file.name


#merge with overcloud.yaml using merge.py. see tripleo-heat-templates
def merge_templates(temp_file_name):
    overcloud_src_path = os.path.abspath(os.path.join(os.path.dirname(
                                  template_path), "overcloud-source.yaml"))
    tmp_file_path = os.path.abspath(temp_file_name)
    template = tht_merge.merge([overcloud_src_path, tmp_file_path], None, None,
                                  included_template_dir=template_path)
    return template
