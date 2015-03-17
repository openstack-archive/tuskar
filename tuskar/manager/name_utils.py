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
Utilities for generating and parsing terms used in the deployment plan,
such as:

* generating a single unique string for a role name/version pairing
* generating the names of each file that will be present in the
  plan, such as the master template, environment file, and each provider
  resource
"""

import os


def generate_role_namespace(role_name, role_version):
    """Creates a unique namespace for the given role name and version.
    The returned namespace can be later converted back into its name and
    version using parse_role_namespace.

    :type role_name: str
    :type role_version: str or int
    :rtype: str
    """
    return '%s-%s' % (role_name, role_version)


def parse_role_namespace(role_namespace):
    """Splits a role's namespace into it's role identification pieces. This
    method should be used in conjunction with generate_role_namespace.

    :type role_namespace: str
    :return: tuple of role name and version
    :rtype: (str, str)
    """
    return role_namespace.rsplit('-', 1)


def role_template_filename(role_name, role_version, role_relative_path):
    """Generates the filename a role's template should be stored in when
    creating the deployment plan's Heat files.

    :type role_name: str
    :type role_version: str
    :type role_relative_path: str or None
    :rtype: str
    """
    namespace = generate_role_namespace(role_name, role_version)

    filename = 'provider-%s.yaml' % namespace
    if role_relative_path:
        filename = os.path.join(role_relative_path, filename)

    return filename


def master_template_filename(plan_name):
    """Generates the filename of a deployment plan's master template when
    it is written out as a Heat template.

    :type plan_name: str
    :rtype: str
    """
    return '%s-%s' % (plan_name, 'template.yaml')


def environment_filename(plan_name):
    """Generates the filename of a deployment plan's environment file
    when it is written out as a file for Heat.

    :type plan_name: str
    :rtype: str
    """
    return '%s-%s' % (plan_name, 'environment.yaml')
