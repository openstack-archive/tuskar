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

"""Tuskar base exception handling.

Includes decorator for re-raising Tuskar-type exceptions.

SHOULD include dedicated exception logging.
"""

from oslo.config import cfg
import six

from tuskar.openstack.common.gettextutils import _  # noqa
from tuskar.openstack.common import log as logging


LOG = logging.getLogger(__name__)

exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help='make exception message format errors fatal'),
]

CONF = cfg.CONF
CONF.register_opts(exc_log_opts)


def _cleanse_dict(original):
    """Strip all admin_password, new_pass, rescue_pass keys from a dict."""
    return dict((k, v) for k, v in original.iteritems() if "_pass" not in k)


class TuskarException(Exception):
    """Base Tuskar Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.message % kwargs

            except Exception as e:
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception(_('Exception in string format operation'))
                for name, value in kwargs.iteritems():
                    LOG.error("%s: %s" % (name, value))

                if CONF.fatal_exception_format_errors:
                    raise e
                else:
                    # at least get the core message out if something happened
                    message = self.message

        super(TuskarException, self).__init__(message)

    def format_message(self):
        if self.__class__.__name__.endswith('_Remote'):
            return self.args[0]
        else:
            return six.text_type(self)


class Invalid(TuskarException):
    message = _("Invalid.")
    code = 400


class NotAuthorized(TuskarException):
    message = _("Not authorized.")
    code = 403


class AdminRequired(NotAuthorized):
    message = _("User does not have admin privileges")


class PolicyNotAuthorized(NotAuthorized):
    message = _("Policy doesn't allow %(action)s to be performed.")


class NotFound(TuskarException):
    message = _("Resource could not be found.")
    code = 404


class OvercloudRoleNotFound(NotFound):
    message = _('Overcloud role could not be found.')


class OvercloudRoleCountNotFound(NotFound):
    message = _('Overcloud role count could not be found.')


class OvercloudNotFound(NotFound):
    message = _('Overcloud could not be found.')


class DuplicateEntry(TuskarException):
    message = _("Duplicate entry found.")
    code = 409


class OvercloudRoleExists(DuplicateEntry):
    message = _("Overcloud role with name %(name)s already exists.")


class OvercloudRoleInUse(Invalid):
    message = _('Role %(name)s is in use by an overcloud.')


class OvercloudRoleCountExists(DuplicateEntry):
    message = _("Count for overcloud %(cloud)s and "
                "role %(role)s already exists.")


class OvercloudExists(DuplicateEntry):
    message = _("Overcloud with name %(name)s already exists.")


class DuplicateAttribute(DuplicateEntry):
    message = _("One or more attributes is duplicated for the overcloud.")


class ConfigNotFound(TuskarException):
    message = _("Could not find config at %(path)s")


class StackNotFound(NotFound):
    message = _("The Stack for this Overcloud can't be found.")


class StackAlreadyCreated(DuplicateEntry):
    message = _("The Stack for this Overcloud already exists.")


class ParseCountsAndFlavorsFailed(DuplicateEntry):
    message = _("Parsing of counts and flavors from roles failed.")


class HeatTemplateCreateFailed(Invalid):
    message = _("The Heat template failed to create.")


class HeatTemplateValidateFailed(Invalid):
    message = _("Validation of the Heat template failed.")


class HeatStackProcessingAttributesFailed(Invalid):
    message = _("Processing of Heat stack attributes failed")


class HeatStackUpdateFailed(Invalid):
    message = _("The Heat stack failed to update.")


class HeatStackCreateFailed(Invalid):
    message = _("The Heat stack failed to update.")


class HeatStackDeleteFailed(Invalid):
    message = _("The Heat stack failed to delete.")


class PlanNotFound(NotFound):
    message = _('Plan could not be found.')


class PlanExists(DuplicateEntry):
    message = _("Plan with name %(name)s already exists.")
