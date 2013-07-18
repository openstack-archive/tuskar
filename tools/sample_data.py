#!/usr/bin/env python

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
# Copyright 2013 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# Using the REST API, populates the DB with some sample data
# Based on python-ceilometerclient/ceilometerclient/common/http.py

import httplib
import json
import logging
import socket
import urlparse
import uuid

LOG = logging.getLogger(__name__)


def log_curl_request(conn, base_url, url, method, kwargs):
    curl = ['curl -i -X %s' % method]

    for (key, value) in kwargs['headers'].items():
        header = '-H \'%s: %s\'' % (key, value)
        curl.append(header)

    if 'body' in kwargs:
        curl.append('-d \'%s\'' % kwargs['body'])

    curl.append('http://%s:%d%s%s' % (conn.host, conn.port, base_url, url))
    LOG.debug(' '.join(curl))


def log_http_response(resp, body=None):
    status = (resp.version / 10.0, resp.status, resp.reason)
    dump = ['\nHTTP/%.1f %s %s' % status]
    dump.extend(['%s: %s' % (k, v) for k, v in resp.getheaders()])
    dump.append('')
    if body:
        dump.extend([body, ''])
    LOG.debug('\n'.join(dump))


def make_connection_url(base_url, url):
    return '%s/%s' % (base_url.rstrip('/'), url.lstrip('/'))


def http_request(conn, base_url, url, method, **kwargs):
    log_curl_request(conn, base_url, url, method, kwargs)

    try:
        conn_url = make_connection_url(base_url, url)
        conn.request(method, conn_url, **kwargs)
        resp = conn.getresponse()
    except socket.gaierror as e:
        message = ('Error finding address for %(url)s: %(e)s' %
                   {'url': url, 'e': e})
        raise RuntimeError(message)
    except (socket.error, socket.timeout) as e:
        message = ('Error communicating with %(endpoint)s %(e)s' %
                   {'endpoint': 'http://%s:%d' % (conn.host, conn.port),
                    'e': e})
        raise RuntimeError(message)

    if 300 <= resp.status < 600:
        LOG.warn('Request returned failure/redirect status.')
        raise RuntimeError('Status code %d returned' % resp.status)

    body = resp.read()

    log_http_response(resp, body)

    return resp, body


def json_request(conn, base_url, url, method, **kwargs):
    kwargs.setdefault('headers', {})
    kwargs['headers'].setdefault('Content-Type', 'application/json')
    kwargs['headers'].setdefault('Accept', 'application/json')

    if 'body' in kwargs:
        kwargs['body'] = json.dumps(kwargs['body'])

    resp, body = http_request(conn, base_url, url, method, **kwargs)
    content_type = resp.getheader('content-type', None)

    if resp.status == 204 or resp.status == 205 or content_type is None:
        body = None
    elif 'application/json' in content_type:
        try:
            body = json.loads(body)
        except ValueError:
            LOG.error('Could not decode response body as JSON')
    else:
        body = None

    return resp, body


def create_resource_class(conn, base_url, name, service_type):
    return json_request(conn, base_url, '/resource_classes', 'POST',
                        body=dict(name=name, service_type=service_type))


def create_rack(conn, base_url, name, slots, subnet, capacities):
    return json_request(conn, base_url, '/racks', 'POST',
                        body=dict(name=name, slots=slots, subnet=subnet,
                                  capacities=capacities))


def set_nodes_on_rack(conn, base_url, rack_url, nodes):
    return json_request(conn, base_url, rack_url, 'PUT',
                        body=dict(nodes=nodes))


def create_flavor(conn, base_url, resource_class_url, flavor):
    return json_request(conn, base_url + resource_class_url, '/flavors', 'PUT', body=flavor)


def get_location(base_url, resp):
    return urlparse.urlparse(resp.getheader('location')).path[len(base_url):]


def generate_uuid():
    return str(uuid.uuid4())


if __name__ == '__main__':
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    conn = httplib.HTTPConnection('localhost', 6385)

    base_url = '/v1'

    resp, body = create_resource_class(conn, base_url,
                                       name='m1', service_type='compute')
    m1_url = get_location(base_url, resp)

    capacities = [
        dict(name='total_cpu', value='12', unit='count'),
        dict(name='total_memory', value='3072', unit='MB'),
    ]
    resp, body = create_rack(conn, base_url,
                             name='rack1', slots=30,
                             subnet='192.168.1.0/24',
                             capacities=capacities)
    rack1_url = get_location(base_url, resp)

    nodes = []
    while len(nodes) < 30:
        nodes.append(dict(id=generate_uuid()))
    set_nodes_on_rack(conn, base_url, rack1_url, nodes)

    flavors = [
        dict(name='m1.small',
             capacities=[
                dict(name='cpu', value='1', unit='count'),
                dict(name='memory', value='1.7', unit='GB'),
                dict(name='storage', value='160', unit='GB'),
             ]),
        dict(name='m1.medium',
             capacities=[
                dict(name='cpu', value='1', unit='count'),
                dict(name='memory', value='3.75', unit='GB'),
                dict(name='storage', value='410', unit='GB'),
             ]),
        dict(name='m1.large',
             capacities=[
                dict(name='cpu', value='2', unit='count'),
                dict(name='memory', value='7.5', unit='GB'),
                dict(name='storage', value='840', unit='GB'),
             ]),
        dict(name='m1.xlarge',
             capacities=[
                dict(name='cpu', value='4', unit='count'),
                dict(name='memory', value='15', unit='GB'),
                dict(name='storage', value='1680', unit='GB'),
             ]),
    ]
    for flavor in flavors:
        create_flavor(conn, base_url, m1_url, flavor)
