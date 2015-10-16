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

import flask
from oslo_config import cfg
from oslo_log import log
from oslo_utils import uuidutils
import werkzeug

CONF = cfg.CONF
CONF.debug = True

app = flask.Flask(__name__)
LOG = log.getLogger('tripleo_common.api.main')

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
        except werkzeug.exceptions.HTTPException as exc:
            return error_response(exc, exc.code or 400)
        except Exception as exc:
            LOG.exception('Internal server error')
            msg = 'Internal server error'  # TODO i18n
            if CONF.debug:
                msg += ' (%s): %s' % (exc.__class__.__name__, exc)
            return error_response(msg)

    return wrapper


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
    # plans = tripleo_common.get_plans
    # return flask.jsonify({'plans': plans})


@app.route('/v3/plans/<plan_name>', methods=['DELETE', 'GET', 'PATCH', 'POST'])
@convert_exceptions
def api_plan(plan_name):
    if flask.request.method == 'POST':
        # plan_files = flask.request.json['plan_files']
        # tripleo_common.create_plan(plan_name, plan_files)
        return flask.jsonify(message="Creating Plan {0}".format(plan_name))
    elif: flask.request.method == 'GET':
        # plan = tripleo_common.get_plan(plan_name)
        # return flask.jsonify({'plan': plan})
    elif: flask.request.method == 'PATCH':
        # plan_files = flask.request.json['plan_files']
        # tripleo_common.update_plan(plan_name, plan_files)
        return flask.jsonify(message="Updating Plan {0}".format(plan_name))
    else:
        # tripleo_common.delete_plan(plan_name)
        return flask.jsonify(message="Deleting Plan {0}".format(plan_name))


@app.route('/v3/plans/<plan_name>/resource_types', methods=['GET', 'POST'])
@convert_exceptions
def api_plan_resource_types(plan_name):
    if flask.request.method == 'POST':
        # resource_types = flask.request.json['resource_types']
        # tripleo_common.update_plan_resource_types(plan_name, resource_types)
        return flask.jsonify(message="Updating Plan {0} Resource Types".format(plan_name))
    else:
        # resource_types = tripleo_common.get_plan_resource_types(plan_name)
        # return flask.jsonify({'resource_types': resource_types})


@app.route('/v3/plans/<plan_name>/parameters', methods=['GET', 'POST'])
@convert_exceptions
def api_plan_parameters(plan_name):
    if flask.request.method == 'POST':
        # parameters = flask.request.json['parameters']
        # tripleo_common.update_plan_parameters(plan_name, parameters)
        return flask.jsonify(message="Updating Plan {0} Parameters".format(plan_name))
    else:
        # parameters = tripleo_common.get_plan_parameters(plan_name)
        # return flask.jsonify({'parameters': parameters})


@app.route('/v3/plans/<plan_name>/roles', methods=['GET'])
@convert_exceptions
def get_plan_roles(plan_name):
    # roles = tripleo_common.get_plan_roles(plan_name)
    # return flask.jsonify({'roles': roles})


@app.route('/v3/plans/<plan_name>/validate', methods=['GET'])
@convert_exceptions
def validate_plan(plan_name):
    # validation = tripleo_common.validate_plan(plan_name)
    # return flask.jsonify({'validation': validation})


@app.route('/v3/plans/<plan_name>/deploy', methods=['POST'])
@convert_exceptions
def deploy_plan(plan_name):
    # tripleo_common.deploy_plan(plan_name)
    return flask.jsonify(message="Deploying Plan {0}".format(plan_name))


if __name__ == '__main__':
    app.debug = True
    # TODO: get port from config
    app.run(port=8585)
