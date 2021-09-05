from __future__ import annotations
from typing import List, Tuple, Dict
from app.main import app
from fastapi.testclient import TestClient
import unittest
import json
import re
from datetime import datetime


class MainTest(unittest.TestCase):

	def test_get_0(self):
		_app = TestClient(app)
		_response = _app.get("/v1/test/get")
		self.assertEqual(200, _response.status_code)
		self.assertEqual({"is_successful": True, "response": None, "error": None}, _response.json())

	def test_post_0(self):
		_app = TestClient(app)
		_response = _app.post("/v1/test/post")
		self.assertEqual(200, _response.status_code)
		self.assertEqual({"is_successful": True, "response": None, "error": None}, _response.json())

	def test_json_0(self):
		_app = TestClient(app)
		_response = _app.post("/v1/test/json", json={"test": "hello"})
		self.assertEqual(200, _response.status_code)
		self.assertEqual({"is_successful": True, "response": {"test": "hello"}, "error": None}, _response.json())

	def test_announce_device_0(self):
		_app = TestClient(app)
		_response = _app.post("/v1/device/announce", json={"device_guid": "2061BABC-9CCE-4E48-9C7C-C09D92342678", "purpose_guid": "866FB619-E643-46CB-B508-1377EF43CEBC"})
		self.assertEqual(200, _response.status_code)
		_response_json = _response.json()
		self.assertTrue(_response_json["is_successful"])
		self.assertIsNone(_response_json["error"])
		self.assertIsNotNone(_response_json["response"])
		self.assertIsNotNone(_response_json["response"]["device"])
		self.assertEqual("2061BABC-9CCE-4E48-9C7C-C09D92342678", _response_json["response"]["device"]["device_guid"])
		self.assertEqual("866FB619-E643-46CB-B508-1377EF43CEBC", _response_json["response"]["device"]["purpose_guid"])

	def test_full_transmission_path_0(self):
		# create transmission, dequeuer asks again, fails, reporter asks again, complete with retry, dequeuer fails, report completes without retry, dequeuer finds nothing

		_app = TestClient(app)

		# introduce source device

		_first_device_guid = "805FC328-943D-42BA-A81D-8486ADE0C4A1"
		_first_device_purpose_guid = "71779DF6-B7AB-4815-9308-CD688B3F2F0D"
		_response = _app.post("/v1/device/announce", json={"device_guid": _first_device_guid, "purpose_guid": _first_device_purpose_guid})
		self.assertEqual(200, _response.status_code)
		_first_device = _response.json()["response"]["device"]
		self.assertIsNotNone(_first_device)
		self.assertEqual(_first_device_guid, _first_device["device_guid"])
		self.assertEqual(_first_device_purpose_guid, _first_device["purpose_guid"])

		# introduce destination device

		_second_device_guid = "FB144F0B-8A53-49E4-85A5-5349EAB4FBF1"
		_second_device_purpose_guid = "B5155325-C1D6-4ED8-A7B4-BF52601D326C"
		_response = _app.post("/v1/device/announce", json={"device_guid": _second_device_guid, "purpose_guid": _second_device_purpose_guid})
		self.assertEqual(200, _response.status_code)
		_second_device = _response.json()["response"]["device"]
		self.assertIsNotNone(_second_device)
		self.assertEqual(_second_device_guid, _second_device["device_guid"])
		self.assertEqual(_second_device_purpose_guid, _second_device["purpose_guid"])

		# pretend that the source device does not know about the destination device

		_response = _app.post("/v1/device/list", params={"purpose_guid": _second_device_purpose_guid})
		self.assertEqual(200, _response.status_code)
		_discovered_destination_devices = _response.json()["response"]["devices"]
		self.assertEqual(1, len(_discovered_destination_devices))
		self.assertEqual(_second_device_guid, _discovered_destination_devices[0]["device_guid"])

		# send transmission from source to device

		_queue_guid = "A0A70E5F-8552-483F-89A9-7D26B91A95BD"
		_first_transmission_json_string = json.dumps({
			"test": True
		})
		_first_transmission_enqueue_post_params = {
			"queue_guid": _queue_guid,
			"source_device_guid": _first_device_guid,
			"transmission_json_string": _first_transmission_json_string,
			"destination_device_guid": _discovered_destination_devices[0]["device_guid"]
		}
		_response = _app.post("/v1/transmission/enqueue", params=_first_transmission_enqueue_post_params)
		self.assertEqual(200, _response.status_code)
		_first_transmission = _response.json()["response"]["transmission"]
		self.assertEqual(_first_transmission_enqueue_post_params["queue_guid"], _first_transmission["queue_guid"])
		self.assertEqual(_first_transmission_enqueue_post_params["source_device_guid"], _first_transmission["source_device_guid"])
		self.assertEqual(_first_transmission_enqueue_post_params["transmission_json_string"], _first_transmission["transmission_json_string"])
		self.assertEqual(_first_transmission_enqueue_post_params["destination_device_guid"], _first_transmission["destination_device_guid"])

		_second_transmission_json_string = json.dumps({
			"test": False
		})
		_second_transmission_enqueue_post_params = {
			"queue_guid": _queue_guid,
			"source_device_guid": _first_device_guid,
			"transmission_json_string": _second_transmission_json_string,
			"destination_device_guid": _discovered_destination_devices[0]["device_guid"]
		}
		_response = _app.post("/v1/transmission/enqueue", params=_second_transmission_enqueue_post_params)
		self.assertEqual(200, _response.status_code)
		_second_transmission = _response.json()["response"]["transmission"]
		self.assertEqual(_second_transmission_enqueue_post_params["queue_guid"], _second_transmission["queue_guid"])
		self.assertEqual(_second_transmission_enqueue_post_params["source_device_guid"], _second_transmission["source_device_guid"])
		self.assertEqual(_second_transmission_enqueue_post_params["transmission_json_string"], _second_transmission["transmission_json_string"])
		self.assertEqual(_second_transmission_enqueue_post_params["destination_device_guid"], _second_transmission["destination_device_guid"])

		# setup dequeuer

		_dequeuer_guid = "20E5EF95-2D4C-44D7-B750-98A413A6613B"

		_dequeuer_before_datetime = datetime.utcnow()
		_response = _app.post("/v1/dequeuer/announce", params={"dequeuer_guid": _dequeuer_guid})
		_dequeuer_after_datetime = datetime.utcnow()
		self.assertEqual(200, _response.status_code)
		_dequeuer = _response.json()["response"]["dequeuer"]
		self.assertEqual(_dequeuer_guid, _dequeuer["dequeuer_guid"])
		self.assertEqual(True, _dequeuer["is_responsive"])
		self.assertLess(_dequeuer_before_datetime, datetime.strptime(_dequeuer["responsive_update_datetime"], "%Y-%m-%d %H:%M:%S.%f"))
		self.assertGreater(_dequeuer_after_datetime, datetime.strptime(_dequeuer["responsive_update_datetime"], "%Y-%m-%d %H:%M:%S.%f"))

		# pull first transmission

		_response = _app.post("/v1/transmission/dequeue", params={"dequeuer_guid": _dequeuer_guid, "queue_guid": _queue_guid})  # TODO
		self.assertEqual(200, _response.status_code)
		_first_transmission_dequeue = _response.json()["response"]["transmission_dequeue"]
		self.assertEqual(_dequeuer_guid, _first_transmission_dequeue["dequeuer_guid"])
		self.assertEqual(_first_transmission["transmission_guid"], _first_transmission_dequeue["transmission_guid"])

		# try to pull again, but receive the same transmission

		_response = _app.post("/v1/transmission/dequeue", params={"dequeuer_guid": _dequeuer_guid, "queue_guid": _queue_guid})
		self.assertEqual(200, _response.status_code)
		_first_again_transmission_dequeue = _response.json()["response"]["transmission_dequeue"]
		self.assertEqual(_dequeuer_guid, _first_again_transmission_dequeue["dequeuer_guid"])
		self.assertEqual(_first_transmission["transmission_guid"], _first_again_transmission_dequeue["transmission_guid"])
		self.assertEqual(_first_transmission_dequeue["transmission_dequeue_guid"], _first_again_transmission_dequeue["transmission_dequeue_guid"])

		# fail dequeue

		_response = _app.post("/v1/transmission/failure", params={"transmission_dequeue_guid": _first_transmission_dequeue["transmission_dequeue_guid"], "error_message_json_string": json.dumps({"error": "first"})})
		self.assertEqual(200, _response.status_code)
		_transmission_dequeue_error_transmission = _response.json()["response"]["transmission_dequeue_error_transmission"]
		self.assertEqual(_first_transmission_dequeue["transmission_dequeue_guid"], _transmission_dequeue_error_transmission["transmission_dequeue_guid"])
		self.assertEqual(json.dumps({"error": "first"}), _transmission_dequeue_error_transmission["error_message_json_string"], )

		# setup reporter

		_reporter_guid = "CF56EBB0-0BC1-4122-822D-C8BE6A2E6D63"

		_reporter_before_datetime = datetime.utcnow()
		_response = _app.post("/v1/reporter/announce", params={"reporter_guid": _reporter_guid})
		_reporter_after_datetime = datetime.utcnow()
		self.assertEqual(200, _response.status_code)
		_reporter = _response.json()["response"]["reporter"]
		self.assertEqual(_reporter_guid, _reporter["reporter_guid"])
		self.assertEqual(True, _reporter["is_responsive"])
		self.assertLess(_reporter_before_datetime, datetime.strptime(_reporter["responsive_update_datetime"], "%Y-%m-%d %H:%M:%S.%f"))
		self.assertGreater(_reporter_after_datetime, datetime.strptime(_reporter["responsive_update_datetime"], "%Y-%m-%d %H:%M:%S.%f"))

		# pull first failure

		_response = _app.post("/v1/failure/dequeue", params={"reporter_guid": _reporter_guid, "queue_guid": _queue_guid})
		self.assertEqual(200, _response.status_code)
		_first_transmission_dequeue_error_transmission_dequeue = _response.json()["response"]["transmission_dequeue_error_transmission_dequeue"]
		self.assertIsNotNone(_first_transmission_dequeue_error_transmission_dequeue)
		self.assertEqual(_transmission_dequeue_error_transmission["transmission_dequeue_error_transmission_guid"], _first_transmission_dequeue_error_transmission_dequeue["transmission_dequeue_error_transmission_guid"])
		self.assertEqual("testclient", _first_transmission_dequeue_error_transmission_dequeue["destination_client"]["ip_address"])

		_response = _app.post("/v1/failure/dequeue", params={"reporter_guid": _reporter_guid, "queue_guid": _queue_guid})
		self.assertEqual(200, _response.status_code)
		_first_again_transmission_dequeue_error_transmission_dequeue = _response.json()["response"]["transmission_dequeue_error_transmission_dequeue"]
		self.assertIsNotNone(_first_again_transmission_dequeue_error_transmission_dequeue)
		self.assertEqual(_first_transmission_dequeue_error_transmission_dequeue["transmission_dequeue_error_transmission_dequeue_guid"], _first_again_transmission_dequeue_error_transmission_dequeue["transmission_dequeue_error_transmission_dequeue_guid"])

		# complete the failed transaction and setup for retry

		_response = _app.post("/v1/failure/complete", params={"transmission_dequeue_error_transmission_dequeue_guid": _first_transmission_dequeue_error_transmission_dequeue["transmission_dequeue_error_transmission_dequeue_guid"], "is_retry_requested": True})
		self.assertEqual(200, _response.status_code)

		# pull the first transaction again, but the destination needs to announce itself first

		_response = _app.post("/v1/transmission/dequeue", params={"dequeuer_guid": _dequeuer_guid, "queue_guid": _queue_guid})
		self.assertEqual(200, _response.status_code)
		_first_again_transmission_dequeue = _response.json()["response"]["transmission_dequeue"]
		self.assertIsNone(_first_again_transmission_dequeue)

		# reannounce destination device

		_response = _app.post("/v1/device/announce", json={"device_guid": _second_device_guid, "purpose_guid": _second_device_purpose_guid})
		self.assertEqual(200, _response.status_code)
		_second_device = _response.json()["response"]["device"]
		self.assertIsNotNone(_second_device)
		self.assertEqual(_second_device_guid, _second_device["device_guid"])
		self.assertEqual(_second_device_purpose_guid, _second_device["purpose_guid"])

		# dequeue first transaction again

		_response = _app.post("/v1/transmission/dequeue", params={"dequeuer_guid": _dequeuer_guid, "queue_guid": _queue_guid})
		self.assertEqual(200, _response.status_code)
		_first_again_transmission_dequeue = _response.json()["response"]["transmission_dequeue"]
		self.assertEqual(_dequeuer_guid, _first_again_transmission_dequeue["dequeuer_guid"])
		self.assertEqual(_first_transmission["transmission_guid"], _first_again_transmission_dequeue["transmission_guid"])
		self.assertNotEqual(_first_transmission_dequeue["transmission_dequeue_guid"], _first_again_transmission_dequeue["transmission_dequeue_guid"])

		# fail dequeue

		_response = _app.post("/v1/transmission/failure", params={"transmission_dequeue_guid": _first_again_transmission_dequeue["transmission_dequeue_guid"], "error_message_json_string": json.dumps({"error": "first"})})
		self.assertEqual(200, _response.status_code)
		_transmission_dequeue_error_transmission = _response.json()["response"]["transmission_dequeue_error_transmission"]
		self.assertEqual(_first_again_transmission_dequeue["transmission_dequeue_guid"], _transmission_dequeue_error_transmission["transmission_dequeue_guid"])
		self.assertEqual(json.dumps({"error": "first"}), _transmission_dequeue_error_transmission["error_message_json_string"], )

		# pull first failure

		_response = _app.post("/v1/failure/dequeue", params={"reporter_guid": _reporter_guid, "queue_guid": _queue_guid})
		self.assertEqual(200, _response.status_code)
		_first_transmission_dequeue_error_transmission_dequeue = _response.json()["response"]["transmission_dequeue_error_transmission_dequeue"]
		self.assertIsNotNone(_first_transmission_dequeue_error_transmission_dequeue)
		self.assertEqual(_transmission_dequeue_error_transmission["transmission_dequeue_error_transmission_guid"], _first_transmission_dequeue_error_transmission_dequeue["transmission_dequeue_error_transmission_guid"])
		self.assertEqual("testclient", _first_transmission_dequeue_error_transmission_dequeue["destination_client"]["ip_address"])

		# fail the failed transaction

		_response = _app.post("/v1/failure/failure", params={"transmission_dequeue_error_transmission_dequeue_guid": _first_transmission_dequeue_error_transmission_dequeue["transmission_dequeue_error_transmission_dequeue_guid"], "error_message_json_string": json.dumps({"something": "here"})})
		self.assertEqual(200, _response.status_code)

		# try to pull a transmission, but the failed failure still needs to be addressed

		_response = _app.post("/v1/transmission/dequeue", params={"dequeuer_guid": _dequeuer_guid, "queue_guid": _queue_guid})  # TODO
		self.assertEqual(200, _response.status_code)
		_first_transmission_dequeue = _response.json()["response"]["transmission_dequeue"]
		self.assertIsNone(_first_transmission_dequeue)

		# try to dequeue failed transmission, but nothing to find since existing transmission is still in failed state

		_response = _app.post("/v1/failure/dequeue", params={"reporter_guid": _reporter_guid, "queue_guid": _queue_guid})
		self.assertEqual(200, _response.status_code)
		_first_transmission_dequeue_error_transmission_dequeue = _response.json()["response"]["transmission_dequeue_error_transmission_dequeue"]
		self.assertIsNone(_first_transmission_dequeue_error_transmission_dequeue)

		# reannounce source device

		_response = _app.post("/v1/device/announce", json={"device_guid": _first_device_guid, "purpose_guid": _first_device_purpose_guid})
		self.assertEqual(200, _response.status_code)
		_first_again_device = _response.json()["response"]["device"]
		self.assertIsNotNone(_first_again_device)
		self.assertEqual(_first_device["device_guid"], _first_again_device["device_guid"])
		self.assertEqual(_first_device["purpose_guid"], _first_again_device["purpose_guid"])

		# pull first failure again so that it can be completed

		_response = _app.post("/v1/failure/dequeue", params={"reporter_guid": _reporter_guid, "queue_guid": _queue_guid})
		self.assertEqual(200, _response.status_code)
		_first_transmission_dequeue_error_transmission_dequeue = _response.json()["response"]["transmission_dequeue_error_transmission_dequeue"]
		self.assertIsNotNone(_first_transmission_dequeue_error_transmission_dequeue)
		self.assertEqual(_transmission_dequeue_error_transmission["transmission_dequeue_error_transmission_guid"], _first_transmission_dequeue_error_transmission_dequeue["transmission_dequeue_error_transmission_guid"])
		self.assertEqual("testclient", _first_transmission_dequeue_error_transmission_dequeue["destination_client"]["ip_address"])

		# complete the failed transaction and cancel

		_response = _app.post("/v1/failure/complete", params={"transmission_dequeue_error_transmission_dequeue_guid": _first_transmission_dequeue_error_transmission_dequeue["transmission_dequeue_error_transmission_dequeue_guid"], "is_retry_requested": False})
		self.assertEqual(200, _response.status_code)

		# try to pull a transmission

		_response = _app.post("/v1/transmission/dequeue", params={"dequeuer_guid": _dequeuer_guid, "queue_guid": _queue_guid})  # TODO
		self.assertEqual(200, _response.status_code)
		_first_transmission_dequeue = _response.json()["response"]["transmission_dequeue"]
		self.assertIsNotNone(_first_transmission_dequeue)
		self.assertNotEqual(_first_again_transmission_dequeue["transmission_guid"], _first_transmission_dequeue["transmission_guid"])

		# complete transmission

		_response = _app.post("/v1/transmission/complete", params={"transmission_dequeue_guid": _first_transmission_dequeue["transmission_dequeue_guid"]})
		self.assertEqual(200, _response.status_code)

	def test_get_uuid_0(self):
			_app = TestClient(app)
			_response = _app.post("/v1/uuid")
			self.assertEqual(200, _response.status_code)
			_uuid = _response.json()["response"]["uuid"]
			_match = re.search("^[A-F0-9]{8}\\-[A-F0-9]{4}\\-[A-F0-9]{4}\\-[A-F0-9]{4}\\-[A-F0-9]{12}$", _uuid)
			self.assertIsNotNone(_match)
