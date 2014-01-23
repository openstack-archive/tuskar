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


LOG = logging.getLogger(__name__)


class ResourceCategoriesController(rest.RestController):
    """REST controller for the ResourceCategory class."""

    @wsme.validate(models.ResourceCategory)
    @wsme_pecan.wsexpose(models.ResourceCategory,
                         body=models.ResourceCategory,
                         status_code=201)
    def post(self, transfer_category):
        """Creates a new resource category.

        :param transfer_category: data submitted by the user
        :type  transfer_category:
               tuskar.api.controllers.v1.models.ResourceCategory

        :return: created category
        :rtype:  tuskar.api.controllers.v1.models.ResourceCategory

        :raises: tuskar.common.exception.ResourceCategoryExists: if a resource
                 category with the given name exists
        """

        LOG.debug('Creating resource category: %s' % transfer_category)

        # Persist to the database
        db_category = transfer_category.to_db_model()
        result = pecan.request.dbapi.create_resource_category(db_category)

        # Package for transfer back to the user
        saved_category =\
            models.ResourceCategory.from_db_model(result)

        return saved_category

    @wsme.validate(models.ResourceCategory)
    @wsme_pecan.wsexpose(models.ResourceCategory,
                         int,
                         body=models.ResourceCategory)
    def put(self, category_id, category_delta):

        LOG.debug('Updating resource category: %s' % category_id)

        # ID is in the URL so make sure it's in the transfer object
        # before translation
        category_delta.id = category_id

        db_delta = category_delta.to_db_model(omit_unset=True)

        # Will raise a not found if there is no category with the ID
        updated = pecan.request.dbapi.update_resource_category(db_delta)

        return updated

    @wsme_pecan.wsexpose(None, int, status_code=204)
    def delete(self, category_id):
        """Deletes the given resource category.

        :param category_id: identifies the category being deleted
        :type  category_id: int

        :raises: tuskar.common.exception.ResourceCategoryNotFound if there
                 is no category with the given ID
        """

        LOG.debug('Deleting resource category with ID: %s' % category_id)
        pecan.request.dbapi.delete_resource_category_by_id(category_id)

    @wsme_pecan.wsexpose(models.ResourceCategory, int)
    def get_one(self, category_id):
        """Returns a specific resource category.

        An exception is raised if no resource category is found with the
        given ID.

        :param category_id: identifies the category being deleted
        :type  category_id: int

        :return: matching resource category
        :rtype:  tuskar.api.controllers.v1.models.ResourceCategory

        :raises: tuskar.common.exception.ResourceCategoryNotFound if there
                 is no category with the given ID
        """

        LOG.debug('Retrieving resource category with ID: %s' % category_id)
        category = pecan.request.dbapi.get_resource_category_by_id(category_id)
        transfer_category = models.ResourceCategory.from_db_model(category)
        return transfer_category

    @wsme_pecan.wsexpose([models.ResourceCategory])
    def get_all(self):
        """Returns all resource categories.

        An empty list is returned if no resource categories are present.

        :return: list of categories; empty list if none are found
        :rtype:  list of tuskar.api.controllers.v1.models.ResourceCategory
        """
        LOG.debug('Retrieving all resource categories')
        categories = pecan.request.dbapi.get_resource_categories()
        transfer_categories = [models.ResourceCategory.from_db_model(c)
                               for c in categories]
        return transfer_categories
