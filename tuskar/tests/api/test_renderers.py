# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from mock import Mock
from mock import patch
from wsme.api import Response

from tuskar.api.renderers import JSONRenderer
from tuskar.tests.api.api import FunctionalTest


class JSONRendererTests(FunctionalTest):

    def setUp(self):
        super(JSONRendererTests, self).setUp()
        self.renderer = JSONRenderer(None, None)

    @patch('wsme.rest.json.encode_result')
    def test_2XX_response(self, encode_result):
        """Test a standard response dict containing the type and result set."""

        datatype = Mock()
        result = Mock()

        self.renderer.render('', {
            'datatype': datatype,
            'result': result
        })

        # Verify the wsme json result encoder (encode_result) is called with
        # the correct values.
        encode_result.assert_called_once_with(result, datatype)

    @patch('pecan.response')
    @patch('wsme.rest.json.encode_error')
    def test_pecan_response(self, encode_error, response):
        """Test that a wsme Response instance renders correctly."""

        # Create a Mock that has the properties we need of the Response class.
        datatype = Mock()
        result = Mock(spec=Response)
        result.status_code = 418
        result.obj = Mock()
        result.obj.faultstring = "Failed"
        result.obj.debuginfo = "Information"

        # Test
        self.renderer.render('', {
            'datatype': datatype,
            'result': result
        })

        # Verify the wsme json error encoder (encode_error) is called with the
        # correctly structured response
        encode_error.assert_called_once_with(None, {
            'identityFault': {
                'message': 'Failed',
                'code': 418,
                'details': 'Information'
            }
        })

    @patch('wsme.rest.json.encode_error')
    def test_500_response(self, encode_error):
        """Test that internal Exceptions return correctly structures JSON."""

        # Recreate the dictionary provided by pecan on user code exceptions.
        namespace = {
            'debuginfo': None,
            'faultcode': 'Server',
            'faultstring': "Exception message"
        }

        # Test
        self.renderer.render('', namespace)

        # Verify the wsme json error encoder (encode_error) is called with the
        # correctly structured response
        encode_error.assert_called_once_with(None, {
            'identityFault': {
                'message': "Exception message",
                'code': 500,
                'details': None
            }
        })
