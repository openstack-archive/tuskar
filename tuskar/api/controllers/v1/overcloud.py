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
from pecan import rest
import wsme
from wsmeext import pecan as wsme_pecan

from tuskar.api.controllers.v1 import models
from tuskar.heat.client import HeatClient as heat_client
import tuskar.heat.template_tools as template_tools

LOG = logging.getLogger(__name__)

TEMP_RCS = {'resource_categories': {'controller': 1, 'compute': 1}}

class OvercloudsController(rest.RestController):
    """REST controller for the Overcloud class."""

    TEMP_RCS = {'resource_categories': {'controller': 1, 'compute': 1}}

    TEMP_PARAMS_LIST = {
        'AdminToken'             : 'c5166331806d761c92b6f491f0e3f909e5639a37',
        'AdminPassword'          : '067e24d0d2d82930b41bb933a730d6e30be5adb4',
        'CinderPassword'         : '117aeb8cc919a998b860a8ee57d347f4eae5822d',
        'GlancePassword'         : '2f90c38d4ce7a04e71b56b2f2fd7b7bfe10f8e58',
        'HeatPassword'           : '24c8326d35078d30ded8032ebafeeda92c983958',
        'NeutronPassword'        : '2a73e61eb2592c3104f6d6355f5622cb0982c3ab',
        'NovaPassword'           : 'bf064f4a66eea26e9cef66186430fadd8bbfe0bb',
        'NeutronPublicInterface' : 'eth0',
        'SwiftPassword'          : 'f20b5065f142b739ae14b326a35851a987368386',
        'SwiftHashSuffix'        : '89bae3856e96ca7c2f0d61ee66574193c7862edb',
        'NovaComputeLibvirtType' : 'qemu'}

    _custom_actions = {'template_get': ['GET'], 'template_deploy':['POST']}

    @pecan.expose()
    def template_get(self):
        rcs = self.TEMP_RCS
        #keep it super simple at first       'object': 1, 'block': 2}}
        #categories = pecan.request.dbapi.get_resource_categories()
        categories = []
        overcloud = template_tools.merge_templates(rcs)
        return overcloud

    @pecan.expose()
    def template_deploy(self):
        rcs = self.TEMP_RCS
        #keep it super simple at first       'object': 1, 'block': 2}}
        #categories = pecan.request.dbapi.get_resource_categories()
        categories = []
        overcloud = template_tools.merge_templates(rcs)
        print (overcloud)
        heat = heat_client()
        #keeping this for now until heat client methods are reworked:
        params = {}
        if heat.validate_template(overcloud):
            params = self.TEMP_PARAMS_LIST
            if heat.exists_stack():
                res = heat.update_stack(overcloud, params)
            else:
                res = heat.create_stack(overcloud, params)

            if res:
                pecan.response.status_code = 202
                return {}
            else:
                raise wsme.exc.ClientSideError(_(
                    "Cannot update the Heat overcloud template"
                ))
        else:
            raise wsme.exc.ClientSideError(_("The overcloud Heat template"
                                             "could not be validated"))

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

        return updated

    @wsme_pecan.wsexpose(None, int, status_code=204)
    def delete(self, overcloud_id):
        """Deletes the given overcloud.

        :param overcloud_id: identifies the overcloud being deleted
        :type  overcloud_id: int

        :raises: tuskar.common.exception.OvercloudNotFound if there
                 is no overcloud with the given ID
        """

        LOG.debug('Deleting overcloud with ID: %s' % overcloud_id)
        pecan.request.dbapi.delete_overcloud_by_id(overcloud_id)

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
        #"""Returns all overclouds.

        #An empty list is returned if no overclouds are present.

        #:return: list of overclouds; empty list if none are found
        #:rtype:  list of tuskar.api.controllers.v1.models.Overcloud
        #"""
        LOG.debug('Retrieving all overclouds')
        overclouds = pecan.request.dbapi.get_overclouds()
        transfer_overclouds = [models.Overcloud.from_db_model(o)
                               for o in overclouds]
        return transfer_overclouds
