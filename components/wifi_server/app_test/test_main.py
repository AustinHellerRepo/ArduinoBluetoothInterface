from __future__ import annotations
from typing import List, Tuple, Dict
from app.main import app
from fastapi.testclient import TestClient
import unittest
import json
import re
from datetime import datetime
import time
from austin_heller_repo.socket import ServerSocket, ClientSocket


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
		# normal
		_app = TestClient(app)
		_response = _app.post("/v1/device/announce", json={"device_guid": "2061BABC-9CCE-4E48-9C7C-C09D92342678", "purpose_guid": "866FB619-E643-46CB-B508-1377EF43CEBC", "socket_port": 25866})
		self.assertEqual(200, _response.status_code)
		_response_json = _response.json()
		self.assertIsNone(_response_json["error"])
		self.assertTrue(_response_json["is_successful"])
		self.assertIsNotNone(_response_json["response"])
		self.assertIsNotNone(_response_json["response"]["device"])
		self.assertEqual("2061BABC-9CCE-4E48-9C7C-C09D92342678", _response_json["response"]["device"]["device_guid"])
		self.assertEqual("866FB619-E643-46CB-B508-1377EF43CEBC", _response_json["response"]["device"]["purpose_guid"])

	def test_announce_device_1(self):
		# no purpose
		_app = TestClient(app)
		_response = _app.post("/v1/device/announce", json={"device_guid": "2061BABC-9CCE-4E48-9C7C-C09D92342678", "purpose_guid": None, "socket_port": 25866})
		self.assertEqual(200, _response.status_code)
		_response_json = _response.json()
		self.assertIsNone(_response_json["error"])
		self.assertTrue(_response_json["is_successful"])
		self.assertIsNotNone(_response_json["response"])
		self.assertIsNotNone(_response_json["response"]["device"])
		self.assertEqual("2061BABC-9CCE-4E48-9C7C-C09D92342678", _response_json["response"]["device"]["device_guid"])
		self.assertEqual(None, _response_json["response"]["device"]["purpose_guid"])

	def test_full_transmission_path_0(self):
		# create transmission, dequeuer asks again, fails, reporter asks again, complete with retry, dequeuer fails, report completes without retry, dequeuer finds nothing

		_app = TestClient(app)

		# introduce source device

		_first_device_socket_port = 27544

		_first_received_transmission = None

		def _first_on_accepted_client_method(client_socket: ClientSocket):
			_json = client_socket.read()
			print(f"_json: {_json}")

		_first_server_socket = ServerSocket(
			to_client_packet_bytes_length=4096,
			listening_limit_total=10,
			accept_timeout_seconds=0.1,
			client_read_failed_delay_seconds=0.1
		)
		_first_server_socket.start_accepting_clients(
			host_ip_address="0.0.0.0",
			host_port=_first_device_socket_port,
			on_accepted_client_method=_first_on_accepted_client_method
		)

		_first_device_guid = "805FC328-943D-42BA-A81D-8486ADE0C4A1"
		_first_device_purpose_guid = "71779DF6-B7AB-4815-9308-CD688B3F2F0D"
		_response = _app.post("/v1/device/announce", json={"device_guid": _first_device_guid, "purpose_guid": _first_device_purpose_guid, "socket_port": _first_device_socket_port})
		self.assertEqual(200, _response.status_code)
		_first_device = _response.json()["response"]["device"]
		self.assertIsNotNone(_first_device)
		self.assertEqual(_first_device_guid, _first_device["device_guid"])
		self.assertIsNotNone(_first_device["instance_guid"])
		self.assertEqual(_first_device_purpose_guid, _first_device["purpose_guid"])

		# introduce destination device

		_second_device_socket_port = 23221

		_second_received_transmission = None

		def _second_on_accepted_client_method(client_socket: ClientSocket):
			_json = client_socket.read()
			print(f"_json: {_json}")

		_second_server_socket = ServerSocket(
			to_client_packet_bytes_length=4096,
			listening_limit_total=10,
			accept_timeout_seconds=0.1,
			client_read_failed_delay_seconds=0.1
		)
		_second_server_socket.start_accepting_clients(
			host_ip_address="0.0.0.0",
			host_port=_second_device_socket_port,
			on_accepted_client_method=_second_on_accepted_client_method
		)

		_second_device_guid = "FB144F0B-8A53-49E4-85A5-5349EAB4FBF1"
		_second_device_purpose_guid = "B5155325-C1D6-4ED8-A7B4-BF52601D326C"
		_response = _app.post("/v1/device/announce", json={"device_guid": _second_device_guid, "purpose_guid": _second_device_purpose_guid, "socket_port": _second_device_socket_port})
		self.assertEqual(200, _response.status_code)
		_second_device = _response.json()["response"]["device"]
		self.assertIsNotNone(_second_device)
		self.assertEqual(_second_device_guid, _second_device["device_guid"])
		self.assertIsNotNone(_second_device["instance_guid"])
		self.assertEqual(_second_device_purpose_guid, _second_device["purpose_guid"])

		# pretend that the source device does not know about the destination device

		_response = _app.post("/v1/device/list", json={"purpose_guid": _second_device_purpose_guid})
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
			"source_device_guid": _first_device["device_guid"],
			"source_device_instance_guid": _first_device["instance_guid"],
			"transmission_json_string": _first_transmission_json_string,
			"destination_device_guid": _discovered_destination_devices[0]["device_guid"],
			"destination_device_instance_guid": _discovered_destination_devices[0]["instance_guid"]
		}
		_response = _app.post("/v1/transmission/send_json", json=_first_transmission_enqueue_post_params)
		self.assertEqual(200, _response.status_code)
		_response_json = _response.json()
		self.assertIsNone(_response_json["error"])
		self.assertTrue(_response_json["is_successful"])
		_first_transmission = _response_json["response"]["transmission"]
		self.assertEqual(_first_transmission_enqueue_post_params["queue_guid"], _first_transmission["queue_guid"])
		self.assertEqual(_first_transmission_enqueue_post_params["source_device_guid"], _first_transmission["source_device_guid"])
		self.assertEqual(_first_transmission_enqueue_post_params["destination_device_guid"], _first_transmission["destination_device_guid"])

		_second_transmission_json_string = json.dumps({
			"test": False
		})
		_second_transmission_enqueue_post_params = {
			"queue_guid": _queue_guid,
			"source_device_guid": _first_device["device_guid"],
			"source_device_instance_guid": _first_device["instance_guid"],
			"transmission_json_string": _second_transmission_json_string,
			"destination_device_guid": _discovered_destination_devices[0]["device_guid"],
			"destination_device_instance_guid": _discovered_destination_devices[0]["instance_guid"]
		}
		_response = _app.post("/v1/transmission/send_json", json=_second_transmission_enqueue_post_params)
		self.assertEqual(200, _response.status_code)
		_second_transmission = _response.json()["response"]["transmission"]
		self.assertEqual(_second_transmission_enqueue_post_params["queue_guid"], _second_transmission["queue_guid"])
		self.assertEqual(_second_transmission_enqueue_post_params["source_device_guid"], _second_transmission["source_device_guid"])
		self.assertEqual(_second_transmission_enqueue_post_params["destination_device_guid"], _second_transmission["destination_device_guid"])

		# ensure that the first transmission was received

		time.sleep(5)

		raise NotImplementedError()

	def test_get_uuid_0(self):
		_app = TestClient(app)
		_response = _app.post("/v1/uuid")
		self.assertEqual(200, _response.status_code)
		_uuid = _response.json()["response"]["uuid"]
		_match = re.search("^[A-F0-9]{8}\\-[A-F0-9]{4}\\-[A-F0-9]{4}\\-[A-F0-9]{4}\\-[A-F0-9]{12}$", _uuid)
		self.assertIsNotNone(_match)

	def test_sending_notification_to_dequeuer_0(self):
		# create source, destination, and dequeuer then enqueue one message
		_app = TestClient(app)

		# introduce source device

		_first_device_guid = "805FC328-943D-42BA-A81D-8486ADE0C4A1"
		_first_device_purpose_guid = "71779DF6-B7AB-4815-9308-CD688B3F2F0D"
		_first_device_socket_port = 27544
		_response = _app.post("/v1/device/announce", json={"device_guid": _first_device_guid, "purpose_guid": _first_device_purpose_guid, "socket_port": _first_device_socket_port})
		self.assertEqual(200, _response.status_code)
		_first_device = _response.json()["response"]["device"]
		self.assertIsNotNone(_first_device)
		self.assertEqual(_first_device_guid, _first_device["device_guid"])
		self.assertEqual(_first_device_purpose_guid, _first_device["purpose_guid"])

		# introduce destination device

		_second_device_guid = "FB144F0B-8A53-49E4-85A5-5349EAB4FBF1"
		_second_device_purpose_guid = "B5155325-C1D6-4ED8-A7B4-BF52601D326C"
		_second_device_socket_port = 23221
		_response = _app.post("/v1/device/announce", json={"device_guid": _second_device_guid, "purpose_guid": _second_device_purpose_guid, "socket_port": _second_device_socket_port})
		self.assertEqual(200, _response.status_code)
		_second_device = _response.json()["response"]["device"]
		self.assertIsNotNone(_second_device)
		self.assertEqual(_second_device_guid, _second_device["device_guid"])
		self.assertEqual(_second_device_purpose_guid, _second_device["purpose_guid"])

		# pretend that the source device does not know about the destination device

		_response = _app.post("/v1/device/list", json={"purpose_guid": _second_device_purpose_guid})
		self.assertEqual(200, _response.status_code)
		_discovered_destination_devices = _response.json()["response"]["devices"]
		self.assertEqual(1, len(_discovered_destination_devices))
		self.assertEqual(_second_device_guid, _discovered_destination_devices[0]["device_guid"])

		# setup dequeuer

		_dequeuer_guid = "10C54083-FBC2-4777-A8EA-CF26EDFD24EB"

		_dequeuer_before_datetime = datetime.utcnow()
		_response = _app.post("/v1/dequeuer/announce", json={"dequeuer_guid": _dequeuer_guid, "is_informed_of_enqueue": True, "listening_port": 26733})
		_dequeuer_after_datetime = datetime.utcnow()
		self.assertEqual(200, _response.status_code)
		_dequeuer = _response.json()["response"]["dequeuer"]
		self.assertEqual(_dequeuer_guid, _dequeuer["dequeuer_guid"])
		self.assertEqual(True, _dequeuer["is_responsive"])
		self.assertLess(_dequeuer_before_datetime, datetime.strptime(_dequeuer["responsive_update_datetime"], "%Y-%m-%d %H:%M:%S.%f"))
		self.assertGreater(_dequeuer_after_datetime, datetime.strptime(_dequeuer["responsive_update_datetime"], "%Y-%m-%d %H:%M:%S.%f"))

		_queue_guid = "AB6CC751-2F38-44D8-918D-4FF7F26B213D"
		_first_transmission_json_string = json.dumps({
			"test": True
		})
		_first_transmission_enqueue_post_params = {
			"queue_guid": _queue_guid,
			"source_device_guid": _first_device_guid,
			"transmission_json_string": _first_transmission_json_string,
			"destination_device_guid": _discovered_destination_devices[0]["device_guid"]
		}
		_response = _app.post("/v1/transmission/enqueue", json=_first_transmission_enqueue_post_params)
		self.assertEqual(200, _response.status_code)
		_first_transmission = _response.json()["response"]["transmission"]
		self.assertEqual(_first_transmission_enqueue_post_params["queue_guid"], _first_transmission["queue_guid"])
		self.assertEqual(_first_transmission_enqueue_post_params["source_device_guid"], _first_transmission["source_device_guid"])
		self.assertEqual(_first_transmission_enqueue_post_params["transmission_json_string"], _first_transmission["transmission_json_string"])
		self.assertEqual(_first_transmission_enqueue_post_params["destination_device_guid"], _first_transmission["destination_device_guid"])

		# wait for transmission to be pulled by dequeuer docker container and for failure to transmit to destination to return

		_dequeuer_timeout_seconds = 10.0
		time.sleep(_dequeuer_timeout_seconds)

		# pull first transmission

		_response = _app.post("/v1/transmission/dequeue", json={"dequeuer_guid": _dequeuer_guid, "queue_guid": _queue_guid})  # TODO
		self.assertEqual(200, _response.status_code)
		_first_transmission_dequeue = _response.json()["response"]["transmission_dequeue"]
		self.assertIsNone(_first_transmission_dequeue)  # the dequeue docker container should have pulled this


if __name__ == "__main__":
	unittest.main()
