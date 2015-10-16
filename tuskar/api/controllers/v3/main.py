# Copyright 2015 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import os
import sys

import flask
from keystonemiddleware import auth_token
from oslo_config import cfg
from oslo_log import log
from oslo_middleware import cors
from oslo_utils import uuidutils
#import tripleo_common
import werkzeug

CONF = cfg.CONF
CONF.debug = True

API_SERVICE_OPTS = [
    cfg.StrOpt(
        'tuskar_api_bind_ip',
        default='0.0.0.0',
        help='IP for the Tuskar API server to bind to',
    ),
    cfg.IntOpt(
        'tuskar_api_port',
        default=8585,
        help='The port for the Tuskar API server',
    ),
    cfg.StrOpt(
        'tht_local_dir',
        default='/etc/tuskar/tripleo-heat-templates/',
        help='Local path holding tripleo-heat-templates',
    ),
    cfg.StrOpt(
        'auth_strategy',
        default='keystone',
        help='Method to use for auth: noauth or keystone.'),
]

CONF.register_opts(API_SERVICE_OPTS)

#app = cors.CORS(flask.Flask(__name__), CONF)
app = flask.Flask(__name__)

LOG = log.getLogger('tuskar.api.v3.controllers.main')

MINIMUM_API_VERSION = (1, 0)
CURRENT_API_VERSION = (3, 0)
_MIN_VERSION_HEADER = 'X-OpenStack-TripleO-Common-API-Minimum-Version'
_MAX_VERSION_HEADER = 'X-OpenStack-TripleO-Common-API-Maximum-Version'
_VERSION_HEADER = 'X-OpenStack-TripleO-Common-API-Version'


def _format_version(ver):
    return '%d.%d' % ver


_DEFAULT_API_VERSION = _format_version(CURRENT_API_VERSION)


def create_link_object(urls):
    links = []
    for url in urls:
        links.append({"rel": "self",
                      "href": os.path.join(flask.request.url_root, url)})
    return links


def error_response(exc, code=500):
    res = flask.jsonify(error={'message': str(exc)})
    res.status_code = code
    LOG.debug('Returning error to client: %s', exc)
    return res


def convert_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # except tripleo_common.core.exception.PlanDoesNotExistError as exc:
        #    return error_response(exc, 404)
        except werkzeug.exceptions.HTTPException as exc:
            return error_response(exc, exc.code or 400)
        except Exception as exc:
            LOG.exception('Internal server error')
            msg = 'Internal server error'  # TODO i18n
            if CONF.debug:
                msg += ' (%s): %s' % (exc.__class__.__name__, exc)
            return error_response(msg)

    return wrapper


def get_auth_strategy():
    return CONF.auth_strategy


def check_auth(request):
    """Check authentication on request.

    :param request: Flask request
    :raises: utils.Error if access is denied
    """
    if get_auth_strategy() == 'noauth':
        return
    if request.headers.get('X-Identity-Status').lower() == 'invalid':
        raise Error(_('Authentication required'), code=401)
    roles = (request.headers.get('X-Roles') or '').split(',')
    if 'admin' not in roles:
        LOG.error(_LE('Role "admin" not in user role list %s'), roles)
        raise Error(_('Access denied'), code=403)


@app.before_request
def check_api_version():
    requested = flask.request.headers.get(_VERSION_HEADER,
                                          _DEFAULT_API_VERSION)
    try:
        requested = tuple(int(x) for x in requested.split('.'))
    except (ValueError, TypeError):
        return error_response(_('Malformed API version: expected string '
                                'in form of X.Y'), code=400)

    if requested < MINIMUM_API_VERSION or requested > CURRENT_API_VERSION:
        return error_response(_('Unsupported API version %(requested)s, '
                                'supported range is %(min)s to %(max)s') %
                              {'requested': _format_version(requested),
                               'min': _format_version(MINIMUM_API_VERSION),
                               'max': _format_version(CURRENT_API_VERSION)},
                              code=406)


@app.after_request
def add_version_headers(res):
    res.headers[_MIN_VERSION_HEADER] = '%s.%s' % MINIMUM_API_VERSION
    res.headers[_MAX_VERSION_HEADER] = '%s.%s' % CURRENT_API_VERSION
    return res


@app.route('/', methods=['GET'])
@convert_exceptions
def api_root():
    versions = [
        {
            "status": "CURRENT",
            "id": '%s.%s' % CURRENT_API_VERSION,
        },
    ]

    for version in versions:
        version['links'] = create_link_object(
            ["v%s" % version['id'].split('.')[0]])

    return flask.jsonify(versions=versions)


@app.route('/v3/plans/', methods=['GET'])
@convert_exceptions
def get_plans():
    check_auth(flask.request)
    # plans = tripleo_common.get_plans
    # return flask.jsonify({'plans': plans})


@app.route('/v3/plans/<plan_name>', methods=['DELETE', 'GET', 'PATCH', 'POST'])
@convert_exceptions
def api_plan(plan_name):
    check_auth(flask.request)
    if flask.request.method == 'POST':
        # if not 'plan_files' in flask.request.json:
        #     return error_response('missing plan_files parameter', 400)
        # plan_files = flask.request.json['plan_files']
        # tripleo_common.create_plan(plan_name, plan_files)
        return flask.jsonify(message="Creating Plan {0}".format(plan_name))
    elif flask.request.method == 'PATCH':
        # if not 'plan_files' in flask.request.json:
        #     return error_response('missing plan_files parameter', 400)
        # plan_files = flask.request.json['plan_files']
        # tripleo_common.update_plan(plan_name, plan_files)
        return flask.jsonify(message="Updating Plan {0}".format(plan_name))
    elif flask.request.method == 'GET':
        # plan = tripleo_common.get_plan(plan_name)
        # return flask.jsonify({'plan': plan})
        return flask.jsonify(message="Retrieving Plan {0}".format(plan_name))
    else:
        # tripleo_common.delete_plan(plan_name)
        return flask.jsonify(message="Deleting Plan {0}".format(plan_name))


@app.route('/v3/plans/<plan_name>/resource_types', methods=['GET', 'POST'])
@convert_exceptions
def api_plan_resource_types(plan_name):
    check_auth(flask.request)
    if flask.request.method == 'POST':
        # if not 'resource_types' in flask.request.json:
        #     return error_response('missing resource_types parameter', 400)
        # resource_types = flask.request.json['resource_types']
        # tripleo_common.update_plan_resource_types(plan_name, resource_types)
        return flask.jsonify(message="Updating Plan {0} Resource Types".format(plan_name))
    else:
        # resource_types = tripleo_common.get_plan_resource_types(plan_name)
        # return flask.jsonify({'resource_types': resource_types})
        return flask.jsonify(message="Retrieving Plan {0} Resource Types".format(plan_name))


@app.route('/v3/plans/<plan_name>/parameters', methods=['GET', 'POST'])
@convert_exceptions
def api_plan_parameters(plan_name):
    check_auth(flask.request)
    if flask.request.method == 'POST':
        # if not 'parameters' in flask.request.json:
        #     return error_response('missing parameters parameter', 400)
        # parameters = flask.request.json['parameters']
        # tripleo_common.update_plan_parameters(plan_name, parameters)
        return flask.jsonify(message="Updating Plan {0} Parameters".format(plan_name))
    else:
        # parameters = tripleo_common.get_plan_parameters(plan_name)
        # return flask.jsonify({'parameters': parameters})
        return flask.jsonify(message="Retrieving Plan {0} Parameters".format(plan_name))


@app.route('/v3/plans/<plan_name>/roles', methods=['GET'])
@convert_exceptions
def get_plan_roles(plan_name):
    check_auth(flask.request)
    # roles = tripleo_common.get_plan_roles(plan_name)
    # return flask.jsonify({'roles': roles})
    return flask.jsonify(message="Retrieving Plan {0} Roles".format(plan_name))


@app.route('/v3/plans/<plan_name>/validate', methods=['GET'])
@convert_exceptions
def validate_plan(plan_name):
    check_auth(flask.request)
    # validation = tripleo_common.validate_plan(plan_name)
    # return flask.jsonify({'validation': validation})
    return flask.jsonify(message="Validating Plan {0}".format(plan_name))


@app.route('/v3/plans/<plan_name>/deploy', methods=['POST'])
@convert_exceptions
def deploy_plan(plan_name):
    check_auth(flask.request)
    # tripleo_common.deploy_plan(plan_name)
    return flask.jsonify(message="Deploying Plan {0}".format(plan_name))


def main(args=sys.argv[1:]): # pragma: no cover
    log.register_options(CONF)
    CONF(args, project='tuskar')
    debug = CONF.debug
    log.set_defaults(default_log_levels=[
        'urllib3.connectionpool=WARN',
        'keystonemiddleware.auth_token=WARN',
        'requests.packages.urllib3.connectionpool=WARN'])

    app_kwargs = {'host': CONF.tuskar_api_bind_ip,
                  'port': CONF.tuskar_api_port}

    if get_auth_strategy() != 'noauth':
        auth_conf = dict(CONF.keystone_authtoken)
        auth_conf.update({'admin_password': CONF.keystone_authtoken.admin_password,
                          'admin_user': CONF.keystone_authtoken.admin_user,
                          'auth_uri': CONF.keystone_authtoken.auth_uri,
                          'admin_tenant_name': CONF.keystone_authtoken.admin_tenant_name,
                          'identity_uri': CONF.keystone_authtoken.identity_uri,
                          'delay_auth_decision': True})
        app.wsgi_app = auth_token.AuthProtocol(app.wsgi_app, auth_conf)
    else:
        LOG.warning('Starting unauthenticated, please check'
                        ' configuration')

    app.run(**app_kwargs)


if __name__ == '__main__':
    main()
