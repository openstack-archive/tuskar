#!/usr/bin/env python

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
import six.moves.urllib.parse as urlparse
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

    body = resp.read()
    log_http_response(resp, body)

    if 300 <= resp.status < 600:
        LOG.warn('Request returned failure/redirect status.')
        raise RuntimeError('Status code %d returned' % resp.status)

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


def create_overcloud_role(conn, base_url, name, description, image_name):
    return json_request(conn, base_url, '/overcloud_roles', 'POST',
                        body=dict(name=name, description=description,
                                  image_name=image_name))


def generate_data():
    conn = httplib.HTTPConnection('localhost', 8585)
    base_url = '/v1'

    create_overcloud_role(conn, base_url,
                          name='Controller',
                          description='controller role',
                          image_name='overcloud-control')
    create_overcloud_role(conn, base_url,
                          name='Compute',
                          description='compute role',
                          image_name='overcloud-compute')
    create_overcloud_role(conn, base_url,
                          name='Block Storage',
                          description='block storage role',
                          image_name='overcloud-cinder-volume')
    create_overcloud_role(conn, base_url,
                          name='Object Storage',
                          description='object storage role',
                          image_name='overcloud-swift-storage')


if __name__ == '__main__':
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    generate_data()
