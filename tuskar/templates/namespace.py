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

"""
Methods for manipulating Heat template pieces (parameters, outputs, etc.)
and Heat environment pieces (resource alias) to scope them to a particular
namespace to prevent conflicts when combining templates. This module contains
methods for applying, removing, and testing if a name is part of a
particular namespace.
"""

DELIMITER = '::'

ALIAS_PREFIX = 'Tuskar::'


def apply_template_namespace(namespace, original_name):
    """Applies a namespace to a template component, such as a parameter
    or output.

    :rtype: str
    """
    return namespace + DELIMITER + original_name


def remove_template_namespace(name):
    """Strips any namespace off the given value and returns the original name.

    :rtype: str
    """
    return name[name.index(DELIMITER) + len(DELIMITER):]


def matches_template_namespace(namespace, name):
    """Returns whether or not the given name is in the specified namespace.

    :rtype: bool
    """
    return name.startswith(namespace + DELIMITER)


def apply_resource_alias_namespace(alias):
    """Creates a Heat environment resource alias under the Tuskar namespace.

    :rtype: str
    """
    return ALIAS_PREFIX + alias


def remove_resource_alias_namespace(alias):
    """Returns the original resource alias without the Tuskar namespace.

    :rtype: str
    """
    return alias[len(ALIAS_PREFIX):]
