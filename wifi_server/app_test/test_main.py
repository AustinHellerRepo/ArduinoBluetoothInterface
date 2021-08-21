from __future__ import annotations
from typing import List, Tuple, Dict
from app.main import app
from fastapi.testclient import TestClient
import unittest


class MainTest(unittest.TestCase):

	def test_application_running(self):
		_app = TestClient(app)
		_response = _app.get("/")
		self.assertEqual(200, _response.status_code)
		self.assertEqual({"is_successful": True, "response": None, "error": None}, _response.json())

	def test_announce_device(self):
		_app = TestClient(app)
		_response = _app.post("/v1/device/announce", params={"device_guid": "2061BABC-9CCE-4E48-9C7C-C09D92342678", "purpose_guid": "866FB619-E643-46CB-B508-1377EF43CEBC"})
		self.assertEqual(200, _response.status_code)
		_response_json = _response.json()
		self.assertTrue(_response_json["is_successful"])
		self.assertIsNone(_response_json["error"])
		self.assertIsNotNone(_response_json["response"])
		self.assertIsNotNone(_response_json["response"]["device"])
		self.assertEqual("2061BABC-9CCE-4E48-9C7C-C09D92342678", _response_json["response"]["device"]["device_guid"])
		self.assertEqual("866FB619-E643-46CB-B508-1377EF43CEBC", _response_json["response"]["device"]["purpose_guid"])
	