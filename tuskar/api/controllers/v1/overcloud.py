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
import wsme

from pecan import rest
from wsmeext import pecan as wsme_pecan

from tuskar.api.controllers.v1 import models
from tuskar.common import exception
from tuskar.heat.client import HeatClient
import tuskar.heat.template_tools as template_tools

LOG = logging.getLogger(__name__)


# FIXME(lsmola) this is for debugging purposes only, remove before I3
POC_PARAMS = {'controller': 1, 'compute': 1}

def parse_counts(counts):
    parsed_counts = {}
    for count_obj in counts:
        print pecan.request.dbapi.get_overcloud_role_by_id()
        role = pecan.request.dbapi.get_overcloud_role_by_id(
            count_obj.overcloud_role_id)
        count = count_obj.num_nodes
        parsed_counts[role.image_name] = count

    return parsed_counts

def filter_template_attributes(attributes):
    # TODO(lsmola) make proper filtering
    return {}

def process_stack(attributes, counts, create=False):
    """Helper function for processing the stack. Given a params dict containing
    the Overcloud Roles and initialization parameters create or update the
    stack.

    :param params: Dictionary of initialization params and overcloud roles for
                   heat template and initialization of stack/
    :type  params: dict

    :param create: A flag to designate if we are creating or updating the stack
    :type create: bool
    """

    overcloud = template_tools.merge_templates(parse_counts(counts))
    heat_client = HeatClient()

    stack_exists = heat_client.exists_stack()
    if not heat_client.validate_template(overcloud):
        raise exception.InvalidHeatTemplate()

    if stack_exists and create:
        raise exception.StackAlreadyCreated()

    elif not stack_exists and not create:
        raise exception.StackNotFound()

    res = heat_client.create_stack(overcloud,
                                   filter_template_attributes(attributes))

    if not res:
        if create:
            raise exception.HeatTemplateCreateFailed()

        raise exception.HeatTemplateUpdateFailed()


class OvercloudsController(rest.RestController):
    """REST controller for the Overcloud class."""

    _custom_actions = {'template_get': ['GET']}

    # FIXME(lsmola) this is for debugging purposes only, remove before I3
    @pecan.expose()
    def template_get(self):
        overcloud = template_tools.merge_templates(POC_PARAMS)
        return overcloud

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

        # Persist to the database
        db_overcloud = transfer_overcloud.to_db_model()
        result = pecan.request.dbapi.create_overcloud(db_overcloud)

        # Package for transfer back to the user
        saved_overcloud =\
            models.Overcloud.from_db_model(result)

        # FIXME(lsmola) This is just POC of creating a stack
        # this has to be done properly with proper Work-flow abstraction of:
        # step one- build template and start stack-create
        # step 2- put the right stack_id to the overcloud
        # step 3- initialize the stack
        # step 4- set the correct overcloud status
        process_stack(saved_overcloud.attributes, saved_overcloud.counts,
                      create=True)

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

        updated_overcloud = models.Overcloud.from_db_model(result)

        # FIXME(lsmola) This is just POC of updating a stack
        # this probably should also have workflow
        # step one- build template and stack-update
        # step 2- set the correct overcloud status
        process_stack(updated_overcloud.attributes, updated_overcloud.counts,
                      create=True)

        return updated_overcloud

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
        # step one- delete stack and set status deleting in progress to
        # overcloud
        # step 2 - once stack is deleted, delete the overcloud
        LOG.debug('Deleting overcloud with ID: %s' % overcloud_id)
        pecan.request.dbapi.delete_overcloud_by_id(overcloud_id)

        heat_client = HeatClient()
        if not heat_client.exists_stack():
            # If the stack doesn't exist, we have nothing else to do here.
            return

        result = heat_client.delete_stack()

        if not result:
            raise wsme.exc.ClientSideError(_(
                "Failed to delete the Heat overcloud."
            ))

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
