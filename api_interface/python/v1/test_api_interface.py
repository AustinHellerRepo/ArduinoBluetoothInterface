from __future__ import annotations
from api_interface import ApiInterface
import unittest
import uuid
from datetime import datetime
from typing import List, Tuple, Dict
import json


def get_api_interface() -> ApiInterface:
	return ApiInterface(
		api_base_url="http://0.0.0.0:80"
	)


class ApiInterfaceTest(unittest.TestCase):

	def test_access_api_0(self):
		# attempt to pull from test root
		_api_interface = get_api_interface()
		_test_result = _api_interface.test_root()
		self.assertIsNone(_test_result)

	def test_send_device_annoucement_0(self):
		# send multiple device guids
		_api_interface = get_api_interface()
		_device_guid = str(uuid.uuid4())
		_purpose_guid = str(uuid.uuid4())
		_device_count_per_purpose_guid = {}
		_previous_device_guid = None
		for _index in range(100):
			if _index != 0:
				_previous_device_guid = _device_guid
			if _index % 8 == 0:
				_device_guid = str(uuid.uuid4())
				_purpose_guid = str(uuid.uuid4())
			elif _index % 8 == 1:  # device changes first
				_device_guid = str(uuid.uuid4())
			elif _index % 8 == 2:
				if _purpose_guid in _device_count_per_purpose_guid:
					_device_count_per_purpose_guid[_purpose_guid] -= 1
				_purpose_guid = str(uuid.uuid4())
			elif _index % 8 == 3:
				# change nothing
				pass
			elif _index % 8 == 4:
				_device_guid = str(uuid.uuid4())
				_purpose_guid = str(uuid.uuid4())
			elif _index % 8 == 5:  # purpose changes first
				if _purpose_guid in _device_count_per_purpose_guid:
					_device_count_per_purpose_guid[_purpose_guid] -= 1
				_purpose_guid = str(uuid.uuid4())
			elif _index % 8 == 6:
				_device_guid = str(uuid.uuid4())
			elif _index % 8 == 7:
				# change nothing
				pass

			_send_device_announcement_response = _api_interface.send_device_announcement(
				device_guid=_device_guid,
				purpose_guid=_purpose_guid
			)
			self.assertIsNotNone(_send_device_announcement_response)
			self.assertIn("device", _send_device_announcement_response)
			_device = _send_device_announcement_response["device"]
			self.assertIn("device_guid", _device)
			self.assertEqual(_device_guid, _device["device_guid"])
			self.assertIn("purpose_guid", _device)
			self.assertEqual(_purpose_guid, _device["purpose_guid"])

			if _purpose_guid not in _device_count_per_purpose_guid:
				_device_count_per_purpose_guid[_purpose_guid] = 1
			elif _previous_device_guid != _device_guid:
				_device_count_per_purpose_guid[_purpose_guid] += 1

		_interlaced_purpose_guids = []
		for _purpose_guid_index, _purpose_guid in enumerate(_device_count_per_purpose_guid.keys()):
			_interlaced_purpose_guids.append(str(uuid.uuid4()))
			_interlaced_purpose_guids.append(_purpose_guid)

		for _purpose_guid_index, _purpose_guid in enumerate(_interlaced_purpose_guids):
			_get_available_devices_response = _api_interface.get_available_devices(
				purpose_guid=_purpose_guid
			)
			if _purpose_guid_index % 2 == 0:
				self.assertEqual(0, len(_get_available_devices_response["devices"]))
			else:
				self.assertEqual(_device_count_per_purpose_guid[_purpose_guid], len(_get_available_devices_response["devices"]))

	def test_dequeuer_announcement_0(self):
		# announce a few dequeuers
		_api_interface = get_api_interface()
		for _index in range(100):
			_dequeuer_guid = str(uuid.uuid4())
			_api_interface.send_dequeuer_announcement(
				dequeuer_guid=_dequeuer_guid
			)

	def test_reporter_announcement_0(self):
		# announce a few reporters
		_api_interface = get_api_interface()
		for _index in range(100):
			_reporter_guid = str(uuid.uuid4())
			_api_interface.send_reporter_announcement(
				reporter_guid=_reporter_guid
			)

	def test_send_transmission_0(self):
		# send basic transmission
		_api_interface = get_api_interface()
		_source_device_guid = str(uuid.uuid4())
		_source_device_purpose_guid = str(uuid.uuid4())
		_api_interface.send_device_announcement(
			device_guid=_source_device_guid,
			purpose_guid=_source_device_purpose_guid
		)
		_destination_device_guid = str(uuid.uuid4())
		_destination_device_purpose_guid = str(uuid.uuid4())
		_api_interface.send_device_announcement(
			device_guid=_destination_device_guid,
			purpose_guid=_destination_device_purpose_guid
		)
		_queue_guid = str(uuid.uuid4())
		_transmission_json = {
			"test": True
		}
		_api_interface.send_transmission(
			queue_guid=_queue_guid,
			source_device_guid=_source_device_guid,
			transmission_json=_transmission_json,
			destination_device_guid=_destination_device_guid
		)

		_dequeuer_guid = str(uuid.uuid4())
		_api_interface.send_dequeuer_announcement(
			dequeuer_guid=_dequeuer_guid
		)
		_transmission_dequeue_response = _api_interface.dequeue_next_transmission(
			dequeuer_guid=_dequeuer_guid,
			queue_guid=_queue_guid
		)

		self.assertIn("transmission_dequeue", _transmission_dequeue_response)
		_transmission_dequeue = _transmission_dequeue_response["transmission_dequeue"]
		print(f"_transmission_dequeue: {_transmission_dequeue}")
		self.assertIn("transmission", _transmission_dequeue)
		_transmission = _transmission_dequeue["transmission"]
		self.assertIn("transmission_json_string", _transmission)
		self.assertEqual(json.dumps(_transmission_json), _transmission["transmission_json_string"])
		self.assertEqual(_transmission_json, json.loads(_transmission["transmission_json_string"]))
