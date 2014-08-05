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

import logging

import pecan
from pecan import rest
import six
import wsme
from wsmeext import pecan as wsme_pecan

from tuskar.api.controllers.v1 import models
from tuskar.common import exception
from tuskar.heat.client import HeatClient
import tuskar.heat.template_tools as template_tools

LOG = logging.getLogger(__name__)


def parse_counts_and_flavors(counts, overcloud_roles):
    """Helper for parsing the OvercloudRoleCount object

    Given a list of OvercloudRoleCount and dict of OverlcoudRole objects
    return a dict of (image_name, count) and (image_name, flavor_id) in a
    format used for building a template.

    :param counts: List of tuskar.api.controllers.v1.models.OvercloudRoleCount
    :type  counts: list

    :param overcloud_roles: Dict of (overcloud_role_id, overcloud_role) so
                            we can access image_name and flavor_id of roles
    :type  overcloud_roles: dict

    :return: Tuple of dicts {(image_name, count)}, {(image_name, flavor_id)}
    :rtype:  two dict objects
    """
    parsed_counts = {}
    parsed_flavors = {}
    for count_obj in counts:
        image_name = overcloud_roles[count_obj.overcloud_role_id].image_name
        flavor_id = overcloud_roles[count_obj.overcloud_role_id].flavor_id
        count = count_obj.num_nodes
        parsed_counts[image_name] = count
        parsed_flavors[image_name] = flavor_id

    return parsed_counts, parsed_flavors


def filter_template_attributes(allowed_data, attributes):
    """Helper filtering attributes for template

    Given a list of allowed data and attributes, filter the attributes
    only with keys of allowed data and return filtered data.

    :param allowed_data: Dict of allowed attributes for template returned by
                         validating of template.
    :type  allowed_data: dict

    :param attributes: Dict of attributes sent from user in deploying stack
                       operation
    :type  attributes: Dict

    :return: Dict of filtered attributes
    :rtype:  dict
    """
    allowed_keys = allowed_data.get("Parameters", {}).keys()

    filtered_data = dict([(key, value) for key, value in attributes.items()
                          if key in allowed_keys])

    return filtered_data


def get_overcloud_roles_dict():
    return dict((overcloud_role.id, overcloud_role)
                for overcloud_role in
                pecan.request.dbapi.get_overcloud_roles())


def get_flavor_attributes(parsed_flavors):
    """Helper for building dict of flavor attributes

    Given a dict of parsed flavors, it will put a flavor_ids stored in
    role into attributes that will be fed to heat stack create/update.

    Mapping of image name to flavor_param is stored in template_tools.ROLES.

    :param parsed_flavors: Dict of (image_name, flavor_id)
    :type  parsed_flavors: dict

    :return: Dict of (flavor_param, flavor_id) for Heat Template params
    :rtype:  dict
    """
    flavor_attributes = {}
    for image_name, flavor_id in parsed_flavors.items():
        role = template_tools.ROLES.get(image_name, None)
        if role:
            flavor_param = role['flavor_param']
            flavor_attributes[flavor_param] = flavor_id

    return flavor_attributes


def process_stack(attributes, counts, overcloud_roles, create=False):
    """Helper function for processing the stack.

    Given a params dict containing the Overcloud Roles and initialization
    parameters create or update the stack.

    :param attributes: Dictionary of initialization params and overcloud roles
                       for heat template and initialization of stack
    :type  attributes: dict

    :param counts: Dictionary of counts of roles to be deployed
    :type  counts: dict

    :param overcloud_roles: Dict of (overcloud_role_id, overcloud_role) so
                            we can access image_name and flavor_id of roles
    :type  overcloud_roles: dict

    :param create: A flag to designate if we are creating or updating the stack
    :type create: bool
    """
    heat_client = HeatClient()

    try:
        # Get how many of each role we want and what flavor each role uses.
        parsed_counts, parsed_flavors = parse_counts_and_flavors(
            counts, overcloud_roles)
    except Exception as e:
        raise exception.ParseCountsAndFlavorsFailed(six.text_type(e))

    try:
        # Build the template
        overcloud = template_tools.merge_templates(parsed_counts)
    except Exception as e:
        raise exception.HeatTemplateCreateFailed(six.text_type(e))

    try:
        # Get the parameters that the template accepts and validate
        allowed_data = heat_client.validate_template(overcloud)
    except Exception as e:
        raise exception.HeatTemplateValidateFailed(six.text_type(e))

    stack_exists = heat_client.exists_stack()
    if stack_exists and create:
        raise exception.StackAlreadyCreated()

    elif not stack_exists and not create:
        raise exception.StackNotFound()

    try:
        # Put flavors from OverloudRoles into attributes
        attributes.update(get_flavor_attributes(parsed_flavors))

        # Filter the attributes to allowed only
        filtered_attributes = filter_template_attributes(allowed_data,
                                                         attributes)
    except Exception as e:
        raise exception.HeatStackProcessingAttributesFailed(six.text_type(e))

    if create:
        operation = heat_client.create_stack
    else:
        operation = heat_client.update_stack

    try:
        result = operation(overcloud, filtered_attributes)
    except Exception as e:
        if create:
            raise exception.HeatStackCreateFailed(six.text_type(e))
        else:
            raise exception.HeatStackUpdateFailed(six.text_type(e))

    return result


class OvercloudsController(rest.RestController):
    """REST controller for the Overcloud class."""

    _custom_actions = {'template_parameters': ['GET']}

    @pecan.expose('json')
    def template_parameters(self):
        # TODO(lsmola) returning all possible parameters now, later in J
        # user should pick what to build first and we should return
        # appropriate parameters.
        fixed_params = {template_tools.OVERCLOUD_COMPUTE_ROLE: 1,
                        template_tools.OVERCLOUD_VOLUME_ROLE: 1,
                        template_tools.OVERCLOUD_OBJECT_STORAGE_ROLE: 1}

        # We don't want user to fill flavor based parameters, cause
        # it is already stored in OvercloudRoles, also Image parameters
        # are expected to be default, otherwise our associations
        # will not work.
        except_parameters = ('OvercloudControlFlavor',
                             'OvercloudComputeFlavor',
                             'OvercloudBlockStorageFlavor',
                             'OvercloudSwiftStorageFlavor',
                             'NovaImage',
                             'notcomputeImage',
                             'BlockStorageImage',
                             'SwiftStorageImage',)

        overcloud = template_tools.merge_templates(fixed_params)

        heat_client = HeatClient()
        try:
            allowed_data = heat_client.validate_template(overcloud)
        except Exception as e:
            raise exception.HeatTemplateValidateFailed(unicode(e))

        # Send back only wanted parameters
        template_parameters = dict((key, value) for key, value
                                   in allowed_data['Parameters'].items()
                                   if key not in except_parameters)

        return template_parameters

    @wsme.validate(models.Overcloud)
    @wsme_pecan.wsexpose(models.Overcloud,
                         body=models.Overcloud,
                         status_code=201)
    def post(self, transfer_overcloud):
        """Creates a new overcloud.

        :param transfer_overcloud: data submitted by the user
        :type  transfer_overcloud:
            tuskar.api.controllers.v1.models.Overcloud

        :return: created overcloud
        :rtype:  tuskar.api.controllers.v1.models.Overcloud

        :raises: tuskar.common.exception.OvercloudExists: if an overcloud
                 with the given name exists
        """
        LOG.debug('Creating overcloud: %s' % transfer_overcloud)

        # FIXME(lsmola) This is just POC of creating a stack
        # this has to be done properly with proper Work-flow abstraction of:
        # step 1- build template and start stack-create
        # step 2- put the right stack_id to the overcloud
        # step 3- initialize the stack
        # step 4- set the correct overcloud status
        stack = process_stack(transfer_overcloud.attributes,
                              transfer_overcloud.counts,
                              get_overcloud_roles_dict(),
                              create=True)

        # Persist to the database
        transfer_overcloud.stack_id = stack['stack']['id']
        db_overcloud = transfer_overcloud.to_db_model()
        result = pecan.request.dbapi.create_overcloud(db_overcloud)

        # Package for transfer back to the user
        saved_overcloud = models.Overcloud.from_db_model(result)

        return saved_overcloud

    @wsme.validate(models.Overcloud)
    @wsme_pecan.wsexpose(models.Overcloud,
                         int,
                         body=models.Overcloud)
    def put(self, overcloud_id, overcloud_delta):
        """Updates an existing overcloud, including its attributes and counts.

        :param overcloud_id: identifies the overcloud being deleted
        :type  overcloud_id: int

        :param overcloud_delta: contains only values that are to be affected
               by the update
        :type  overcloud_delta:
            tuskar.api.controllers.v1.models.Overcloud

        :return: created overcloud
        :rtype:  tuskar.api.controllers.v1.models.Overcloud

        :raises: tuskar.common.exception.OvercloudNotFound if there
                 is no overcloud with the given ID
        """
        LOG.debug('Updating overcloud: %s' % overcloud_id)

        # ID is in the URL so make sure it's in the transfer object
        # before translation
        overcloud_delta.id = overcloud_id
        db_delta = overcloud_delta.to_db_model(omit_unset=True)

        # Will raise a not found if there is no overcloud with the ID
        result = pecan.request.dbapi.update_overcloud(db_delta)

        updated_overcloud = models.Overcloud.from_db_model(
            result, mask_passwords=False)

        # FIXME(lsmola) This is just POC of updating a stack
        # this probably should also have workflow
        # step 1- build template and stack-update
        # step 2- set the correct overcloud status
        process_stack(updated_overcloud.attributes, result.counts,
                      get_overcloud_roles_dict())

        return models.Overcloud.from_db_model(result)

    @wsme_pecan.wsexpose(None, int, status_code=204)
    def delete(self, overcloud_id):
        """Deletes the given overcloud.

        :param overcloud_id: identifies the overcloud being deleted
        :type  overcloud_id: int

        :raises: tuskar.common.exception.OvercloudNotFound if there
                 is no overcloud with the given ID
        """

        # FIXME(lsmola) this should always try to delete both overcloud
        # and stack. So it requires some exception catch over below.
        # FIXME(lsmola) there is also a workflow needed
        # step 1- delete stack and set status deleting in progress to
        # overcloud
        # step 2 - once stack is deleted, delete the overcloud
        LOG.debug('Deleting overcloud with ID: %s' % overcloud_id)
        pecan.request.dbapi.delete_overcloud_by_id(overcloud_id)

        heat_client = HeatClient()
        if not heat_client.exists_stack():
            # If the stack doesn't exist, we have nothing else to do here.
            return

        try:
            heat_client.delete_stack()
        except Exception:
            raise exception.HeatStackDeleteFailed()

    @wsme_pecan.wsexpose(models.Overcloud, int)
    def get_one(self, overcloud_id):
        """Returns a specific overcloud.

        An exception is raised if no overcloud is found with the
        given ID.

        :param overcloud_id: identifies the overcloud being deleted
        :type  overcloud_id: int

        :return: matching overcloud
        :rtype:  tuskar.api.controllers.v1.models.Overcloud

        :raises: tuskar.common.exception.OvercloudNotFound if there
                 is no overcloud with the given ID
        """

        LOG.debug('Retrieving overcloud with ID: %s' % overcloud_id)
        overcloud = pecan.request.dbapi.get_overcloud_by_id(overcloud_id)
        transfer_overcloud = models.Overcloud.from_db_model(overcloud)
        return transfer_overcloud

    @wsme_pecan.wsexpose([models.Overcloud])
    def get_all(self):
        """Returns all overclouds.

        An empty list is returned if no overclouds are present.

        :return: list of overclouds; empty list if none are found
        :rtype:  list of tuskar.api.controllers.v1.models.Overcloud
        """
        LOG.debug('Retrieving all overclouds')
        overclouds = pecan.request.dbapi.get_overclouds()
        transfer_overclouds = [models.Overcloud.from_db_model(o)
                               for o in overclouds]
        return transfer_overclouds
