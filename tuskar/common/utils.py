# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Justin Santa Barbara
# Copyright (c) 2012 NTT DOCOMO, INC.
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

"""Utilities and helper functions."""

import os
import re

from oslo.config import cfg

from tuskar.common import exception
from tuskar.openstack.common import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class LazyPluggable(object):
    """A pluggable backend loaded lazily based on some value."""

    def __init__(self, pivot, config_group=None, **backends):
        self.__backends = backends
        self.__pivot = pivot
        self.__backend = None
        self.__config_group = config_group

    def __get_backend(self):
        if not self.__backend:
            if self.__config_group is None:
                backend_name = CONF[self.__pivot]
            else:
                backend_name = CONF[self.__config_group][self.__pivot]
            if backend_name not in self.__backends:
                msg = _('Invalid backend: %s') % backend_name
                raise exception.TuskarException(msg)

            backend = self.__backends[backend_name]
            if isinstance(backend, tuple):
                name = backend[0]
                fromlist = backend[1]
            else:
                name = backend
                fromlist = backend

            self.__backend = __import__(name, None, None, fromlist)
        return self.__backend

    def __getattr__(self, key):
        backend = self.__get_backend()
        return getattr(backend, key)


def is_int_like(val):
    """Check if a value looks like an int."""
    try:
        return str(int(val)) == str(val)
    except Exception:
        return False


def read_cached_file(filename, cache_info, reload_func=None):
    """Read from a file if it has been modified.

    :param cache_info: dictionary to hold opaque cache.
    :param reload_func: optional function to be called with data when
                        file is reloaded due to a modification.

    :returns: data from file

    """
    mtime = os.path.getmtime(filename)
    if not cache_info or mtime != cache_info.get('mtime'):
        LOG.debug("Reloading cached file %s" % filename)
        with open(filename) as fap:
            cache_info['data'] = fap.read()
        cache_info['mtime'] = mtime
        if reload_func:
            reload_func(cache_info['data'])
    return cache_info['data']


def resolve_role_extra_name_from_path(role_extra_path):
    """Get the name we will use to store a role-extra file based on its name

        We want to capture the filename and extension into the name of the
        store role-extra object. The name is constructed by prepending 'extra_'
        and using the final '_' to include the extension. Any paths used before
        the filename are dropped at this point (these are resolved relative to
        a given template, i.e. where they are used and referenced).

        For instance 'hieradata/compute.yaml' is stored as
        'extra_compute_yaml'.
    """
    name_ext = os.path.basename(role_extra_path)
    name, extension = os.path.splitext(name_ext)
    return "extra_%s_%s" % (name, extension.replace('.', ''))


def resolve_template_file_name_from_role_extra_name(role_extra_name):
    """Return the name of the included file based on the role-extra name

        The internal representation for a given role-extra file encodes the
        file extension into the name. For instance 'compute.yaml'
        is stored as 'extra_compute_yaml'. Here, given the stored name,
        return name.extension

        Raises a InvalidTemplateExtraStoredName exception if the given
        role_extra_name doesn't start with 'extra_' as a prefix.

        :param role_extra_name: the name as stored for the role-extra
        :type role_extra_name: string

        :return: the name as used in the template
        :rtype: string

        Returns 'compute.yaml' from 'extra_compute_yaml'.
    """
    if role_extra_name.find("extra_") != 0:
        raise exception.InvalidTemplateExtraStoredName(name=role_extra_name)
    name_extension = role_extra_name.replace('extra_', '').split("_")
    extension = name_extension[-1]
    name = "_".join(name_extension[0:-1])
    if len(extension) > 0:
        return "%s.%s" % (name, extension)
    return name


def resolve_template_extra_data(template, template_extra=[]):
    """Match all occurences of get_file against the stored role-extra data.

        :param template: the given heat template to search for "get_file"(s)
        :type template: tuskar.storage.models.StoredFile

        :param template_extra: a list of all stored role-extra data
        :type template_extra: list of tuskar.storage.models.StoredFile

        :return: a dict of 'name'=>'path' for each matched role-extra
        :rtype: dict

        Using regex, compile a list of all occurences of 'get_file:' in the
        template. Match each of the stored role-extra data based on their name.

        For each match capture the full path as it appears in the template
        and couple it to the name of the role-extra we have on record. For
        example:

            [{'extra_common_yaml': 'hieradata/common.yaml'},
             {'extra_object_yaml': 'hieradata/object.yaml'}]

    """
    included_files = []
    all_get_files = re.findall("get_file:.*\n", template.contents)
    # looks like: ["get_file: hieradata/common.yaml}", ... ]
    for te in template_extra:
        token = resolve_template_file_name_from_role_extra_name(te.name)
        for get_file in all_get_files:
            if re.match("get_file:.*%s[}]*\n" % token, get_file):
                path = get_file.replace("get_file:", "").lstrip().replace(
                    "}", "").rstrip()
                included_files.append({te.name: path})
    return included_files
