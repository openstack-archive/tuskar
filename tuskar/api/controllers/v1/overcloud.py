# -*- encoding: utf-8 -*-
#
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
from tuskar.heat.client import HeatClient
import tuskar.heat.template_tools as template_tools

LOG = logging.getLogger(__name__)


# FIXME(lsmola) mocked params for POC, remove later by real ones
POC_PARAMS = {'overcloud_roles': {'controller': 1, 'compute': 1}}
POC_PARAMS_UPDATE = {'overcloud_roles': {'controller': 1, 'compute': 2}}


def create_stack(params):
    """Helper function for creating the stack.

    :param params: Dictionary of params for heat template
                   and initialization of stack
    :type  overcloud_id: dict

    :return: True or False depending on success
    :rtype:  bool
    """

    overcloud = template_tools.merge_templates(params)
    heat_client = HeatClient()

    # FIXME(lsmola) filter the params for the ones template accepts
    params = {}
    if heat_client.validate_template(overcloud):
        if heat_client.exists_stack():
            raise wsme.exc.ClientSideError(_(
                "Cannot create the Heat overcloud stack, it is "
                "already created"
            ))
        else:
            res = heat_client.create_stack(overcloud, params)

        if res:
            return {}
        else:
            raise wsme.exc.ClientSideError(_(
                "Cannot create the Heat overcloud template"
            ))
    else:
        raise wsme.exc.ClientSideError(_("The overcloud Heat template "
                                         "could not be validated"))


def update_stack(params):
    """Helper function for updating the stack.

    :param params: Dictionary of params for heat template
    :type  overcloud_id: dict

    :return: True or False depending on success
    :rtype:  bool
    """

    overcloud = template_tools.merge_templates(params)
    heat_client = HeatClient()

    # FIXME(lsmola) filter the params for the ones template accepts
    params = {}
    if heat_client.validate_template(overcloud):
        if heat_client.exists_stack():
            res = heat_client.update_stack(overcloud, params)
        else:
            raise wsme.exc.ClientSideError(_(
                "Cannot update the Heat overcloud stack, it is "
                "not created"
            ))

        if res:
            return {}
        else:
            raise wsme.exc.ClientSideError(_(
                "Cannot update the Heat overcloud template"
            ))
    else:
        raise wsme.exc.ClientSideError(_("The overcloud Heat template "
                                         "could not be validated"))


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

        # FIXME(lsmola) there has to be constraint that only one
        # overcloud can be created for now

        # Persist to the database
        db_overcloud = transfer_overcloud.to_db_model()
        result = pecan.request.dbapi.create_overcloud(db_overcloud)

        # Package for transfer back to the user
        saved_overcloud =\
            models.Overcloud.from_db_model(result)

        # FIXME(lsmola) This is just POC of creating a stack
        # this has to be done properly with proper Work-flow abstraction of:
        # step one- build template and stack-create
        # step two initialize the stack
        # step 3- set the correct overcloud status
        create_stack(POC_PARAMS)

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

        updated = models.Overcloud.from_db_model(result)

        # FIXME(lsmola) This is just POC of updating a stack
        # this probably should also have workflow
        # step one- build template and stack-update
        # step 2- set the correct overcloud status
        update_stack(POC_PARAMS_UPDATE)

        return updated

    @wsme_pecan.wsexpose(None, int, status_code=204)
    def delete(self, overcloud_id):
        """Deletes the given overcloud.

        :param overcloud_id: identifies the overcloud being deleted
        :type  overcloud_id: int

        :raises: tuskar.common.exception.OvercloudNotFound if there
                 is no overcloud with the given ID
        """

        # FIXME(lsmola) this should always try to delete both overcloud
        # and stack. So it requires some excpetion catch over below.
        LOG.debug('Deleting overcloud with ID: %s' % overcloud_id)
        pecan.request.dbapi.delete_overcloud_by_id(overcloud_id)

        heat_client = HeatClient()
        if heat_client.exists_stack():
            heat_client.delete_stack()
        else:
            raise wsme.exc.ClientSideError(_(
                "Cannot delete the Heat overcloud stack, it is "
                "not created"
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
