#!/usr/bin/env python
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
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

from __future__ import print_function

from os import listdir
from os import path

from tuskar.storage.exceptions import UnknownName
from tuskar.storage.stores import TemplateStore


def _list_templates(directory):
    """Scan a directory and yield a tuple for all the templates containing the
    template name and the full path to the template.
    """

    if not path.isdir(directory):
        raise ValueError("The given path is not a valid directory.")

    directory = path.abspath(directory)

    for filename in listdir(directory):

        if not filename.endswith("yaml") and not filename.endswith("yml"):
            continue

        yield filename, path.join(directory, filename)


def _read_template(template_path):

    with open(template_path) as template_file:
        return template_file.read()


def _create_or_update(name, contents, store=None):

    if store is None:
        store = TemplateStore()

    try:
        template = store.retrieve_by_name(name)

        if template.contents != contents:
            template = store.update(template.uuid, contents)

        return False, template
    except UnknownName:
        return True, store.create(name, contents)


def load_templates(directory, dry_run=False):
    """Given a directory path, import the YAML template files into the
    TemplateStore. When dry_run=True is passed, run through the templates but
    don't add any to the store.

    The returned tuple contains all the template names and then the names split
    over where were created and updated. On a dry run the first item will
    contain all of the templates found while the second two will be empty lists
    as no files were updated or created.

    :param directory: Directory name containing the templates
    :type  directory: str

    :return: Summary of the results as a tuple with the total count and then
        the names of the created and updated templates.
    :rtype:  tuple(list, list, list)
    """

    all_templates, created, updated = [], [], []

    templates = _list_templates(directory)

    for name, template_path in templates:

        contents = _read_template(template_path)
        all_templates.append(name)

        if dry_run:
            continue

        template_created, _ = _create_or_update(name, contents)

        if template_created:
            created.append(name)
        else:
            updated.append(name)

    return all_templates, created, updated
