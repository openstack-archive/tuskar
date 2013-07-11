# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2010 OpenStack Foundation   # All Rights Reserved.
# Copyright 2013 Red Hat                # All Rights Reserved.

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#    Most of the following was copied shamelessly from nova @
#    https://github.com/openstack/nova/blob/master/nova/image/glance.py
#    It's the way nova talks to glance, though obviously
#    s/python-glanceclient/python-novaclient

#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Implementation of an nova flavor service that uses python-novaclient"""
#
# UNTESTED CODE - CAVEAT EMPTOR
#
#uncomment these as they become necessary/as are used

#from __future__ import absolute_import

#import copy
#import itertools
#import random
#import shutil
#import sys
#import time
#import urlparse

import novaclient
#import glanceclient.exc
from oslo.config import cfg

#uncomment these as they become necessary/as are used
#from tuskar.common import exception
#from tuskar.openstack.common import jsonutils
from tuskar.openstack.common import log as logging
#from tuskar.openstack.common import timeutils

nova_opts = [
    cfg.StrOpt('nova_host',
               default='$my_ip',
               help='default nova hostname or ip'),
    cfg.IntOpt('nova_port',
               default=8774, #FIXME IS THAT RIGHT?
               help='default nova port'),
    cfg.StrOpt('nova_protocol',
                default='http',
                help='Default protocol to use when connecting to glance. '
                     'Set to https for SSL.'),
    cfg.BoolOpt('nova_api_insecure',
                default=False,
                help='Allow to perform insecure SSL (https) requests to '
                     'nova'),
    cfg.IntOpt('nova_num_retries',
               default=0,
               help='Number retries when calling novaclient'),
    ]

LOG = logging.getLogger(__name__)
CONF = cfg.CONF
CONF.register_opts(glance_opts)
CONF.import_opt('auth_strategy', 'nova.api.auth')
CONF.import_opt('my_ip', 'nova.netconf')


def generate_nova_url():
    """Generate the URL to nova."""
    return "%s://%s:%d" % (CONF.nova_protocol, CONF.nova_host,
                           CONF.nova_port)

def _create_nova_client(context, host, port, use_ssl, version=1):
    """Instantiate a new novaclient.Client object."""
    if use_ssl:
        scheme = 'https'
    else:
        scheme = 'http'
    params = {}
    params['insecure'] = CONF.nova_api_insecure
    if CONF.auth_strategy == 'keystone':
        params['token'] = context.auth_token
    endpoint = '%s://%s:%s' % (scheme, host, port)
    return novaclient.Client(str(version), endpoint, **params)

class NovaClientWrapper(object):
    """Nova client wrapper class that implements retries."""

    def __init__(self, context=None, host=None, port=None, use_ssl=False,
                 version=1):
        if host is not None:
            self.client = self._create_static_client(context,
                                                     host, port,
                                                     use_ssl, version)
        else:
            self.client = None
        self.api_servers = None

    def _create_static_client(self, context, host, port, use_ssl, version):
        """Create a client that we'll use for every call."""
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.version = version
        return _create_nova_client(context,
                                     self.host, self.port,
                                     self.use_ssl, self.version)

    def _create_onetime_client(self, context, version):
        """Create a client that will be used for one call."""
        if self.api_servers is None:
            self.api_servers = get_api_servers()
        self.host, self.port, self.use_ssl = self.api_servers.next()
        return _create_nova_client(context,
                                     self.host, self.port,
                                     self.use_ssl, version)

    def call(self, context, version, method, *args, **kwargs):
        """
        Call a nova client method.  If we get a connection error,
        retry the request according to CONF.glance_num_retries.
        """
        retry_excs = (novaclient.exc.ServiceUnavailable,
                novaclient.exc.InvalidEndpoint,
                novaclient.exc.CommunicationError)
        num_attempts = 1 + CONF.nova_num_retries

        for attempt in xrange(1, num_attempts + 1):
            client = self.client or self._create_onetime_client(context,
                                                                version)
            try:
                return getattr(client.flavors, method)(*args, **kwargs)
            except retry_excs as e:
                host = self.host
                port = self.port
                extra = "retrying"
                error_msg = _("Error contacting nova server "
                        "'%(host)s:%(port)s' for '%(method)s', %(extra)s.")
                if attempt == num_attempts:
                    extra = 'done trying'
                    LOG.exception(error_msg, locals())
                    raise exception.novaConnectionFailed(
                            host=host, port=port, reason=str(e))
                LOG.exception(error_msg, locals())
                time.sleep(1)


class NovaFlavorService(object):
    """Provides Management of Flavor resources within Nova."""

    def __init__(self, client=None):
        self._client = client or NovaClientWrapper()

    def detail(self, context, **kwargs):
        """Calls out to Nova for a list of detailed flavor information."""
        params = self._extract_query_params(kwargs)
        try:
            flavors = self._client.call(context, 1, 'list', **params)
        except Exception:
            _reraise_translated_exception()

        _flavors = []
        for flavor in flavors:
                _flavors.append(self._translate_from_nova_flavor(flavor))

        return _flavors

    def _extract_query_params(self, params):
        _params = {}
        accepted_params = ('filters', 'marker', 'limit',
                           'sort_key', 'sort_dir')
        for param in accepted_params:
            if params.get(param):
                _params[param] = params.get(param)

        # ensure filters is a dict
        _params.setdefault('filters', {})
        # NOTE(vish): don't filter out private images
        _params['filters'].setdefault('is_public', 'none')

        return _params

    def show(self, context, flavor_id):
        """Returns a dict with flavor data for the given opaque flavor id."""
        try:
            nova_flavor = self._client.call(context, 1, 'get', flavor_id)
        except Exception:
            _reraise_translated_exception()
        flavor = self._translate_from_nova_flavor(nova_flavor)
        return flavor

    def create(self, context, flavor_meta):
        try:
            nova_flavor = self._client.call(
                context, 1, 'create', flavor_meta)
        except novaclient.exc.HTTPException:
            _reraise_translated_exception()

        return self._translate_from_nova_flavor(nova_flavor)

    def delete(self, context, flavor_id):
        try:
            self._client.call(context, 1, 'delete', flavor_id)
        except novaclient.exc.NotFound:
            raise exception.FlavorNotFound(flavor_id=flavor_id)
        except novaclient.exc.HTTPForbidden:
            raise exception.NotAuthorized(nova_id=nova_id)
        return True

    @staticmethod
    def _translate_from_nova_flavor(nova_flavor):
        flavor = _extract_attributes(nova_flavor)
        return flavor

def _extract_attributes(flavor):
    FLAVOR_ATTRIBUTES = ['id', 'name', 'ram', 'disk', 'vcpus']
    output = {}
    for attr in FLAVOR_ATTRIBUTES:
        output[attr] = getattr(flavor, attr, None)
    return output


def _reraise_translated_exception():
    """Transform the exception but keep its traceback intact."""
    exc_type, exc_value, exc_trace = sys.exc_info()
    new_exc = _translate_plain_exception(exc_value)
    raise new_exc, None, exc_trace

def _translate_plain_exception(exc_value):
    if isinstance(exc_value, (novaclient.exc.Forbidden,
                    novaclient.exc.Unauthorized)):
        return exception.NotAuthorized(exc_value)
    if isinstance(exc_value, novaclient.exc.NotFound):
        return exception.NotFound(exc_value)
    if isinstance(exc_value, novaclient.exc.BadRequest):
        return exception.Invalid(exc_value)
    return exc_value

def get_default_flavor_service():
    return NovaFlavorService()
