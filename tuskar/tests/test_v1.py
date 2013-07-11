"""Base classes for API tests.
"""

import os
from oslo.config import cfg
from tuskar.api import app
from tuskar.tests import base
from tuskar.api import acl
from tuskar.tests import api


class TestRacks(api.FunctionalTest):


    def test_it_returns_valid_404(self):
        response = self.get_json('/invalid_path',
                expect_errors=True,
                headers={"Accept":
                    "application/json"}
                )

        self.assertEqual(response.status_int, 404)

    def test_it_returns_404_for_unknown_rack(self):
        response = self.get_json('/racks/123456',
                expect_errors=True,
                headers={"Accept":
                    "application/json"}
                )

        self.assertEqual(response.status_int, 404)
