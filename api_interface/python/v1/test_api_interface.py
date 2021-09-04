from __future__ import annotations
from api_interface import ApiInterface
import unittest
import uuid
from datetime import datetime
from typing import List, Tuple, Dict


def get_api_interface() -> ApiInterface:
	return ApiInterface(
		api_base_url="http://0.0.0.0:80"
	)


class ApiInterfaceTest(unittest.TestCase):

	def test_access_api(self):
		# attempt to pull from test root
		_api_interface = get_api_interface()
		_test_result = _api_interface.test_root()
		self.assertIsNone(_test_result)
