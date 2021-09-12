from __future__ import annotations
from app.database import Database, Client, Device, Transmission, ApiEntrypoint
import unittest
import sqlite3
from typing import List, Tuple, Dict
import uuid
from datetime import datetime


class DatabaseTest(unittest.TestCase):

	def test_insert_device_0(self):
		# missing client
		with Database() as _database:
			_device = None
			with self.assertRaises(sqlite3.IntegrityError):
				_device = _database.insert_device(
					device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
					client_guid="8D825258-C1A3-43AF-A354-6C2EA7561F53",
					purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
					socket_port=24576
				)
			self.assertIsNone(_device)
			_all_devices = _database.get_all_devices()
			self.assertEqual(0, len(_all_devices))

	def test_insert_device_1(self):
		# nothing missing
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
				socket_port=24576
			)
			self.assertIsNotNone(_device)
			_all_devices = _database.get_all_devices()
			self.assertEqual(1, len(_all_devices))

	def test_insert_device_twice_0(self):
		# nothing different
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
				socket_port=24576
			)
			self.assertIsNotNone(_device)
			_other_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
				socket_port=24576
			)
			self.assertIsNotNone(_other_device)
			self.assertEqual(_device.get_device_guid(), _other_device.get_device_guid())
			self.assertEqual(_device.get_purpose_guid(), _other_device.get_purpose_guid())
			self.assertEqual(_device.get_last_known_client_guid(), _other_device.get_last_known_client_guid())
			self.assertNotEqual(_device.get_last_known_datetime(), _other_device.get_last_known_datetime())
			self.assertNotEqual(_device.to_json(), _other_device.to_json())
			_all_devices = _database.get_all_devices()
			self.assertEqual(1, len(_all_devices))

	def test_insert_device_twice_1(self):
		# purpose different
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_client)
			_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
				socket_port=24576
			)
			self.assertIsNotNone(_device)
			_other_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="C439928B-A339-4550-8E2D-B5583C90FD40",
				socket_port=24576
			)
			self.assertIsNotNone(_other_device)
			self.assertEqual(_device.get_device_guid(), _other_device.get_device_guid())
			self.assertNotEqual(_device.get_purpose_guid(), _other_device.get_purpose_guid())
			self.assertNotEqual(_device.to_json(), _other_device.to_json())
			_is_successful, _database_device = _database.try_get_device(
				device_guid=_device.get_device_guid()
			)
			self.assertTrue(_is_successful)
			self.assertEqual(_device.get_device_guid(), _database_device.get_device_guid())
			self.assertNotEqual(_device.get_purpose_guid(), _database_device.get_purpose_guid())
			self.assertEqual(_other_device.get_purpose_guid(), _database_device.get_purpose_guid())
			self.assertNotEqual(_device.to_json(), _database_device.to_json())
			self.assertEqual(_other_device.to_json(), _database_device.to_json())
			_all_devices = _database.get_all_devices()
			self.assertEqual(1, len(_all_devices))

	def test_insert_device_twice_2(self):
		# purpose and client different
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_client)
			_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
				socket_port=24576
			)
			self.assertIsNotNone(_device)
			_other_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_other_client)
			_other_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_other_client.get_client_guid(),
				purpose_guid="C439928B-A339-4550-8E2D-B5583C90FD40",
				socket_port=24576
			)
			self.assertIsNotNone(_other_device)
			self.assertEqual(_device.get_device_guid(), _other_device.get_device_guid())
			self.assertNotEqual(_device.get_purpose_guid(), _other_device.get_purpose_guid())
			self.assertNotEqual(_device.to_json(), _other_device.to_json())
			_is_successful, _database_device = _database.try_get_device(
				device_guid=_device.get_device_guid()
			)
			self.assertTrue(_is_successful)
			self.assertEqual(_device.get_device_guid(), _database_device.get_device_guid())
			self.assertNotEqual(_device.get_purpose_guid(), _database_device.get_purpose_guid())
			self.assertEqual(_other_device.get_purpose_guid(), _database_device.get_purpose_guid())
			self.assertNotEqual(_device.to_json(), _database_device.to_json())
			self.assertEqual(_other_device.to_json(), _database_device.to_json())
			_all_devices = _database.get_all_devices()
			self.assertEqual(1, len(_all_devices))

	def test_insert_device_twice_3(self):
		# client different
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_client)
			_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
				socket_port=24576
			)
			self.assertIsNotNone(_device)
			_other_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_other_client)
			_other_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_other_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
				socket_port=24576
			)
			self.assertIsNotNone(_other_device)
			self.assertEqual(_device.get_device_guid(), _other_device.get_device_guid())
			self.assertEqual(_device.get_purpose_guid(), _other_device.get_purpose_guid())
			self.assertNotEqual(_device.get_last_known_client_guid(), _other_device.get_last_known_client_guid())
			self.assertNotEqual(_device.get_last_known_datetime(), _other_device.get_last_known_datetime())
			self.assertNotEqual(_device.to_json(), _other_device.to_json())
			_is_successful, _database_device = _database.try_get_device(
				device_guid=_device.get_device_guid()
			)
			self.assertTrue(_is_successful)
			self.assertEqual(_device.get_device_guid(), _database_device.get_device_guid())
			self.assertEqual(_device.get_purpose_guid(), _database_device.get_purpose_guid())
			self.assertEqual(_other_device.get_purpose_guid(), _database_device.get_purpose_guid())
			self.assertNotEqual(_device.to_json(), _database_device.to_json())
			self.assertEqual(_other_device.to_json(), _database_device.to_json())
			_all_devices = _database.get_all_devices()
			self.assertEqual(1, len(_all_devices))

	def test_insert_device_different_0(self):
		# nothing is the same
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_client)
			_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
				socket_port=24576
			)
			self.assertIsNotNone(_device)
			_other_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_other_client)
			_other_device = _database.insert_device(
				device_guid="B3D1577E-2874-4F0C-AFD7-254DB00F47CF",
				client_guid=_other_client.get_client_guid(),
				purpose_guid="B978714F-B6EB-4E6B-83EB-2BD9C702F753",
				socket_port=24576
			)
			self.assertIsNotNone(_other_device)
			self.assertNotEqual(_device.get_device_guid(), _other_device.get_device_guid())
			self.assertNotEqual(_device.get_purpose_guid(), _other_device.get_purpose_guid())
			self.assertNotEqual(_device.to_json(), _other_device.to_json())
			_all_devices = _database.get_all_devices()
			self.assertEqual(2, len(_all_devices))

	def test_insert_device_different_1(self):
		# client is the same
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_client)
			_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
				socket_port=24576
			)
			self.assertIsNotNone(_device)
			_other_device = _database.insert_device(
				device_guid="B3D1577E-2874-4F0C-AFD7-254DB00F47CF",
				client_guid=_client.get_client_guid(),
				purpose_guid="B978714F-B6EB-4E6B-83EB-2BD9C702F753",
				socket_port=24576
			)
			self.assertIsNotNone(_other_device)
			self.assertNotEqual(_device.get_device_guid(), _other_device.get_device_guid())
			self.assertNotEqual(_device.get_purpose_guid(), _other_device.get_purpose_guid())
			self.assertNotEqual(_device.to_json(), _other_device.to_json())
			_all_devices = _database.get_all_devices()
			self.assertEqual(2, len(_all_devices))

	def test_insert_device_different_2(self):
		# client and purpose is the same
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_client)
			_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
				socket_port=24576
			)
			self.assertIsNotNone(_device)
			_other_device = _database.insert_device(
				device_guid="B3D1577E-2874-4F0C-AFD7-254DB00F47CF",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212",
				socket_port=24576
			)
			self.assertIsNotNone(_other_device)
			self.assertNotEqual(_device.get_device_guid(), _other_device.get_device_guid())
			self.assertEqual(_device.get_purpose_guid(), _other_device.get_purpose_guid())
			self.assertNotEqual(_device.to_json(), _other_device.to_json())
			_all_devices = _database.get_all_devices()
			self.assertEqual(2, len(_all_devices))

	def test_insert_client(self):
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_client)

	def test_insert_client_twice_0(self):
		# same ip address
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_client)
			_other_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_other_client)
			self.assertEqual(_client.get_client_guid(), _other_client.get_client_guid())
			self.assertEqual(_client.get_ip_address(), _other_client.get_ip_address())

	def test_insert_client_twice_1(self):
		# different ip address
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_client)
			_other_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_other_client)
			self.assertNotEqual(_client.get_client_guid(), _other_client.get_client_guid())
			self.assertNotEqual(_client.get_ip_address(), _other_client.get_ip_address())

	def test_insert_transmission_0(self):
		# source device, client, and destination device missing
		_transmission = None
		with Database() as _database:
			_queue = _database.insert_queue(
				queue_guid="93DDD4A2-DEB1-4475-9038-258010B6B476"
			)
			with self.assertRaises(sqlite3.IntegrityError):
				_transmission = _database.insert_transmission(
					queue_guid="93DDD4A2-DEB1-4475-9038-258010B6B476",
					source_device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
					client_guid="DDF8DAE4-D0C1-4761-A3D5-6C481D669576",
					transmission_json_string="{ \"test\": true }",
					destination_device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B"
				)
		self.assertIsNone(_transmission)

	def test_insert_transmission_1(self):
		# nothing missing and all different clients
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="6E05F5AD-803E-422F-954B-6FBF0F791E12"
			)
			_transmission = _database.insert_transmission(
				queue_guid="6E05F5AD-803E-422F-954B-6FBF0F791E12",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)

	def test_get_next_transmission_0(self):
		# only one available transmission
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="8487777E-E70C-42E7-BC40-202CED41A441"
			)
			_transmission = _database.insert_transmission(
				queue_guid="8487777E-E70C-42E7-BC40-202CED41A441",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="C03DEC02-79C5-494F-BCA8-0FFA2E2F2ABB",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_dequeuer)
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue)
			self.assertEqual(_transmission.get_transmission_guid(), _get_next_transmission_dequeue.get_transmission_guid())

	def test_get_next_transmission_1(self):
		# two available transmissions from same client
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="B1AD1419-123A-4C28-A3CA-2138EE2C2C90"
			)
			_first_transmission = _database.insert_transmission(
				queue_guid=_queue.get_queue_guid(),
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_second_transmission = _database.insert_transmission(
				queue_guid=_queue.get_queue_guid(),
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"other\": 1 }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_second_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="8A38F5A8-0F3F-42C2-A4E8-8FF6F8FA4AD9",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_dequeuer)
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_get_next_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_get_next_transmission_dequeue.get_transmission_guid())

			# transmission completed

			_database.transmission_completed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_first_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

			# dequeue second transmission

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_second_get_next_transmission_dequeue)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_get_next_transmission_dequeue.get_transmission_guid())

	def test_get_next_transmission_2(self):
		# two available transmissions from different clients
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="A5729E3C-E4C4-4091-8956-46019D6DBA17"
			)
			_first_transmission = _database.insert_transmission(
				queue_guid=_queue.get_queue_guid(),
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_second_transmission = _database.insert_transmission(
				queue_guid=_queue.get_queue_guid(),
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"other\": 1 }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_second_transmission)
			_first_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_first_get_next_client)
			_first_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="A97C06B8-3C61-48AA-AE2F-82E242A2C878",
				is_informed_of_enqueue=False,
				client_guid=_first_get_next_client.get_client_guid()
			)
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_first_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_first_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_get_next_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_get_next_transmission_dequeue.get_transmission_guid())
			_second_get_next_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			self.assertIsNotNone(_second_get_next_client)
			_second_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="37399BE8-1EAA-497D-BA5D-E6581E560466",
				is_informed_of_enqueue=False,
				client_guid=_second_get_next_client.get_client_guid()
			)

			# transmission completed

			_database.transmission_completed(
				client_guid=_first_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_first_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

			# dequeue second transmission

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_second_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_second_get_next_transmission_dequeue)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_get_next_transmission_dequeue.get_transmission_guid())

	def test_get_next_transmission_3(self):
		# two available transmissions from same client but first was not completed yet
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="F132BEB3-C25B-41A4-AC40-AE4C60FA23BE"
			)
			_first_transmission = _database.insert_transmission(
				queue_guid="F132BEB3-C25B-41A4-AC40-AE4C60FA23BE",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_second_transmission = _database.insert_transmission(
				queue_guid="F132BEB3-C25B-41A4-AC40-AE4C60FA23BE",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"other\": 1 }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_second_transmission)
			_first_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_first_get_next_client)
			_first_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="4E3F7F3D-B82F-4434-83C4-DDCF43283F9B",
				is_informed_of_enqueue=False,
				client_guid=_first_get_next_client.get_client_guid()
			)
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_first_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_first_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_get_next_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_get_next_transmission_dequeue.get_transmission_guid())

			# dequeue second transmission

			_second_get_next_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			self.assertIsNotNone(_second_get_next_client)
			_second_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="1CE1A72D-C103-4B14-A81A-DA09F412E337",
				is_informed_of_enqueue=False,
				client_guid=_second_get_next_client.get_client_guid()
			)

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_second_get_next_client.get_client_guid()
			)
			self.assertIsNone(_second_get_next_transmission_dequeue)

	def test_get_next_transmission_4(self):
		# only one available transmission but for second dequeuer in same queue
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="8487777E-E70C-42E7-BC40-202CED41A441"
			)
			self.assertEqual("8487777E-E70C-42E7-BC40-202CED41A441", _queue.get_queue_guid())
			_transmission = _database.insert_transmission(
				queue_guid=_queue.get_queue_guid(),
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_first_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="C03DEC02-79C5-494F-BCA8-0FFA2E2F2ABB",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_dequeuer)
			_second_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="78D5DF3C-552B-4E60-AD14-626FA866D4D6",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_second_dequeuer)
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue)
			self.assertEqual(_transmission.get_transmission_guid(), _get_next_transmission_dequeue.get_transmission_guid())

	def test_get_next_transmission_5(self):
		# only one available transmission but for second dequeuer in different queue
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_first_queue = _database.insert_queue(
				queue_guid="8487777E-E70C-42E7-BC40-202CED41A441"
			)
			self.assertEqual("8487777E-E70C-42E7-BC40-202CED41A441", _first_queue.get_queue_guid())
			_second_queue = _database.insert_queue(
				queue_guid="7DA94A53-A396-4DC7-B8EB-551E777CE691"
			)
			self.assertEqual("7DA94A53-A396-4DC7-B8EB-551E777CE691", _second_queue.get_queue_guid())
			_transmission = _database.insert_transmission(
				queue_guid=_second_queue.get_queue_guid(),
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_first_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="C03DEC02-79C5-494F-BCA8-0FFA2E2F2ABB",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_dequeuer)
			_second_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="78D5DF3C-552B-4E60-AD14-626FA866D4D6",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_second_dequeuer)
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_second_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue)
			self.assertEqual(_transmission.get_transmission_guid(), _get_next_transmission_dequeue.get_transmission_guid())

	def test_transmission_complete_0(self):
		# complete from same client that dequeued
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="3B373B25-2CFB-4CCC-AE1A-4610BF100BE7"
			)
			_transmission = _database.insert_transmission(
				queue_guid="3B373B25-2CFB-4CCC-AE1A-4610BF100BE7",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="97009FE3-10C9-4B39-A472-373C6CAD4126",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue)
			self.assertEqual(_transmission.get_transmission_guid(), _get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_completed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

	def test_transmission_complete_1(self):
		# complete from different client than dequeued
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="AD483656-A2E1-4061-BD4B-D4604DB72958"
			)
			_transmission = _database.insert_transmission(
				queue_guid="AD483656-A2E1-4061-BD4B-D4604DB72958",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="8C19940C-DA62-43CA-93ED-AC9C0BFDD707",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue)
			self.assertEqual(_transmission.get_transmission_guid(), _get_next_transmission_dequeue.get_transmission_guid())
			_complete_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			self.assertIsNotNone(_complete_client)
			_database.transmission_completed(
				client_guid=_complete_client.get_client_guid(),
				transmission_dequeue_guid=_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

	def test_transmission_failed_0(self):
		# same client the dequeued marks as failed
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="A5543D66-0897-4A1C-A232-7617BC70E251"
			)
			_transmission = _database.insert_transmission(
				queue_guid="A5543D66-0897-4A1C-A232-7617BC70E251",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="F9652133-3FFB-4EFF-ADB2-26320E7E0FA6",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue)
			self.assertEqual(_transmission.get_transmission_guid(), _get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_failed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_get_next_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"message\" }"
			)

	def test_transmission_failed_1(self):
		# queue first, pull first, mark failed, and fail to queue second
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="200D4210-E037-4D9E-A8AE-0CF4899E4AC2"
			)
			_first_transmission = _database.insert_transmission(
				queue_guid="200D4210-E037-4D9E-A8AE-0CF4899E4AC2",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="DEFE4C38-0106-4072-AC7F-E9EC43EDD60E",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_get_next_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_failed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_first_get_next_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"message\" }"
			)
			_second_transmission = _database.insert_transmission(
				queue_guid="200D4210-E037-4D9E-A8AE-0CF4899E4AC2",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"second\": \"transmission\" }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNone(_second_get_next_transmission_dequeue)

	def test_transmission_failed_2(self):
		# queue first, pull first, queue second, mark failed, mark failure as complete without retry, pull second, mark completed
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="A3E2A6FE-551C-4413-BF3E-0CDD137912EA"
			)
			_first_transmission = _database.insert_transmission(
				queue_guid="A3E2A6FE-551C-4413-BF3E-0CDD137912EA",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="AB8E2EE3-A1E6-4189-971E-E778ED43808F",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_get_next_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_get_next_transmission_dequeue.get_transmission_guid())
			_second_transmission = _database.insert_transmission(
				queue_guid="A3E2A6FE-551C-4413-BF3E-0CDD137912EA",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"second\": \"transmission\" }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			_database.transmission_failed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_first_get_next_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"message\" }"
			)

			_failed_dequeue_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="70FAC0CB-EA93-404D-8F83-D9B25FAF70B0",
				is_informed_of_enqueue=False,
				client_guid=_failed_dequeue_client.get_client_guid()
			)

			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failed_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)

			_database.failed_transmission_completed(
				client_guid=_failed_dequeue_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=False
			)

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_second_get_next_transmission_dequeue)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_completed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_second_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

	def test_transmission_failed_3(self):
		# queue first, queue second, pull first, mark failed, mark failure as complete without retry, pull second, mark completed
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="05130566-0898-4C62-A1A5-5AC4A484CE02"
			)
			_first_transmission = _database.insert_transmission(
				queue_guid="05130566-0898-4C62-A1A5-5AC4A484CE02",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_second_transmission = _database.insert_transmission(
				queue_guid="05130566-0898-4C62-A1A5-5AC4A484CE02",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"second\": \"transmission\" }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="ECCD5319-92C6-43A4-BC08-1B984BA6C910",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_get_next_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_failed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_first_get_next_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"message\" }"
			)

			_failed_dequeue_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="6D44AA09-F6DE-4A98-893F-DBA0FAA2F78F",
				is_informed_of_enqueue=False,
				client_guid=_failed_dequeue_client.get_client_guid()
			)

			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failed_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)

			_database.failed_transmission_completed(
				client_guid=_failed_dequeue_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=False
			)

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_completed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_second_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

	def test_transmission_failed_4(self):
		# queue first, pull first, mark failed, mark failure as complete without retry, queue second, pull second, mark completed
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="4CFE0AB5-DAA5-48C0-9DB8-F3F26E2C39AA"
			)
			_first_transmission = _database.insert_transmission(
				queue_guid="4CFE0AB5-DAA5-48C0-9DB8-F3F26E2C39AA",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="D84352F4-5E26-4C72-B348-F3B7464E1374",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_get_next_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_failed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_first_get_next_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"message\" }"
			)

			_failed_dequeue_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="17CA30BC-76E0-453A-8C62-F9E1F5672F11",
				is_informed_of_enqueue=False,
				client_guid=_failed_dequeue_client.get_client_guid()
			)

			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failed_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)

			_database.failed_transmission_completed(
				client_guid=_failed_dequeue_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=False
			)

			_second_transmission = _database.insert_transmission(
				queue_guid="4CFE0AB5-DAA5-48C0-9DB8-F3F26E2C39AA",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"second\": \"transmission\" }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_second_get_next_transmission_dequeue)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_completed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_second_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

	def test_transmission_failed_5(self):
		# queue first, pull first, mark failed, mark failure as complete with retry, queue second, fail to pull second
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="0DD4ACB8-C069-4925-84E7-34017F515891"
			)
			_first_transmission = _database.insert_transmission(
				queue_guid="0DD4ACB8-C069-4925-84E7-34017F515891",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="82A7FB93-A228-4632-937F-68F1CB1A26F6",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)

			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_get_next_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_failed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_first_get_next_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"message\" }"
			)

			_failed_dequeue_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="37D4AC01-23A0-4625-BBBB-1F08A82DE4C1",
				is_informed_of_enqueue=False,
				client_guid=_failed_dequeue_client.get_client_guid()
			)

			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failed_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)

			_database.failed_transmission_completed(
				client_guid=_failed_dequeue_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=True
			)

			_second_transmission = _database.insert_transmission(
				queue_guid="0DD4ACB8-C069-4925-84E7-34017F515891",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"second\": \"transmission\" }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNone(_second_get_next_transmission_dequeue)

	def test_transmission_failed_and_transmit_0(self):
		# transmit from same client the dequeued marked as failed and cancel
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="F240877A-E460-474B-B97D-DF5A49698E5C"
			)
			_transmission = _database.insert_transmission(
				queue_guid="F240877A-E460-474B-B97D-DF5A49698E5C",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="B5B999F4-B39F-4CDF-A287-FA658F138430",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue)
			self.assertEqual(_transmission.get_transmission_guid(), _get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_failed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_get_next_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"message\" }"
			)
			_failed_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			self.assertIsNotNone(_failed_client)
			_reporter = _database.insert_reporter(
				reporter_guid="978CEC80-A01D-4BE0-BE85-725C64D62F07",
				is_informed_of_enqueue=False,
				client_guid=_failed_client.get_client_guid()
			)

			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failed_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)
			self.assertEqual(_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid(), _get_next_transmission_dequeue.get_transmission_dequeue_guid())

			# send failure to origin of transmission and receive back if the transmission should be retried

			_database.failed_transmission_completed(
				client_guid=_failed_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=False
			)

			# device connects should not cause the transmission to requeue

			_same_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertEqual(_destination_device.get_device_guid(), _same_device.get_device_guid())
			self.assertEqual(_destination_device.get_purpose_guid(), _same_device.get_purpose_guid())
			self.assertEqual(_destination_device.get_last_known_client_guid(), _same_device.get_last_known_client_guid())
			self.assertNotEqual(_destination_device.get_last_known_datetime(), _same_device.get_last_known_datetime())
			self.assertNotEqual(_destination_device.to_json(), _same_device.to_json())

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNone(_second_get_next_transmission_dequeue)

	def test_transmission_failed_and_transmit_1(self):
		# transmit from same client the dequeued marked as failed and retransmit
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="455BB049-BA72-464D-BD0E-00E71C921A0F"
			)
			_transmission = _database.insert_transmission(
				queue_guid="455BB049-BA72-464D-BD0E-00E71C921A0F",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="A949C1CD-2466-4919-BAEC-92BF1CE1B5A4",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue)
			self.assertEqual(_transmission.get_transmission_guid(), _get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_failed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_get_next_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"message\" }"
			)
			_failed_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			self.assertIsNotNone(_failed_client)
			_reporter = _database.insert_reporter(
				reporter_guid="FCF1D55C-08AE-45CC-AD0E-139F62B48B9A",
				is_informed_of_enqueue=False,
				client_guid=_failed_client.get_client_guid()
			)

			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failed_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)
			self.assertEqual(_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid(), _get_next_transmission_dequeue.get_transmission_dequeue_guid())

			# send failure to origin of transmission and receive back if the transmission should be retried

			_database.failed_transmission_completed(
				client_guid=_failed_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=True
			)

			# device connects should cause the transmission to requeue

			_same_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertEqual(_destination_device.get_device_guid(), _same_device.get_device_guid())
			self.assertEqual(_destination_device.get_purpose_guid(), _same_device.get_purpose_guid())
			self.assertEqual(_destination_device.get_last_known_client_guid(), _same_device.get_last_known_client_guid())
			self.assertNotEqual(_destination_device.get_last_known_datetime(), _same_device.get_last_known_datetime())
			self.assertNotEqual(_destination_device.to_json(), _same_device.to_json())

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_second_get_next_transmission_dequeue)
			self.assertEqual(_second_get_next_transmission_dequeue.get_transmission_guid(), _get_next_transmission_dequeue.get_transmission_guid())

	def test_transmission_failed_and_transmit_2(self):
		# transmit from same client the dequeued marked as failed and retransmit before queued transmission
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="F91A3C4A-917D-4D3A-ADF8-61DA3973F6EC"
			)
			_transmission = _database.insert_transmission(
				queue_guid="F91A3C4A-917D-4D3A-ADF8-61DA3973F6EC",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="099D4BA3-CCA9-4834-9E83-4D4BE60DCB29",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)

			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue)
			self.assertEqual(_transmission.get_transmission_guid(), _get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_failed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_get_next_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"message\" }"
			)
			_failed_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			self.assertIsNotNone(_failed_client)
			_reporter = _database.insert_reporter(
				reporter_guid="764C68C1-D6CE-4207-B9A7-E4E6FC4844C5",
				is_informed_of_enqueue=False,
				client_guid=_failed_client.get_client_guid()
			)

			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failed_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)
			self.assertEqual(_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid(), _get_next_transmission_dequeue.get_transmission_dequeue_guid())

			# another transmission is queued up before the failed transmission is sent back to the origin

			_second_transmission = _database.insert_transmission(
				queue_guid="F91A3C4A-917D-4D3A-ADF8-61DA3973F6EC",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"after_failure\": \"yup\" }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_second_transmission)

			# dequeuing the second transmission should fail because the destination has a failed transmission

			_first_attempt_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNone(_first_attempt_second_transmission_dequeue)

			# send failure to origin of transmission and receive back if the transmission should be retried

			_database.failed_transmission_completed(
				client_guid=_failed_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=True
			)

			# device connects should cause the transmission to requeue

			_same_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertEqual(_destination_device.get_device_guid(), _same_device.get_device_guid())
			self.assertEqual(_destination_device.get_purpose_guid(), _same_device.get_purpose_guid())
			self.assertEqual(_destination_device.get_last_known_client_guid(), _same_device.get_last_known_client_guid())
			self.assertNotEqual(_destination_device.get_last_known_datetime(), _same_device.get_last_known_datetime())
			self.assertNotEqual(_destination_device.to_json(), _same_device.to_json())

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_second_get_next_transmission_dequeue)
			self.assertEqual(_second_get_next_transmission_dequeue.get_transmission_guid(), _get_next_transmission_dequeue.get_transmission_guid())

			# complete first transmission

			_database.transmission_completed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_second_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

			# now the second transmission can be dequeued

			_second_attempt_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_second_attempt_second_transmission_dequeue)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_attempt_second_transmission_dequeue.get_transmission_guid())

	def test_multiple_sources_and_multiple_destinations_0(self):
		# queue up ring of multiple transmissions and then dequeue/complete in order
		with Database() as _database:
			_clients = []  # type: List[Client]
			_devices = []  # type: List[Device]
			for _index in range(10):
				_client = _database.insert_client(
					ip_address=f"127.0.0.{_index + 1}"
				)
				_device = _database.insert_device(
					device_guid=str(uuid.uuid4()),
					client_guid=_client.get_client_guid(),
					purpose_guid=str(uuid.uuid4()),
					socket_port=24576
				)
				_clients.append(_client)
				_devices.append(_device)
			_queue = _database.insert_queue(
				queue_guid="74D37EC1-43EF-4B9D-8BEB-D6966762BC11"
			)
			_transmissions = []  # type: List[Transmission]
			for _index in range(len(_devices)**2):
				_source_index = _index % len(_devices)
				_destination_index = (_index + 1) % len(_devices)
				_transmission = _database.insert_transmission(
					queue_guid="74D37EC1-43EF-4B9D-8BEB-D6966762BC11",
					source_device_guid=_devices[_source_index].get_device_guid(),
					client_guid=_clients[_source_index].get_client_guid(),
					transmission_json_string=f"{{ \"transmission\": {_index} }}",
					destination_device_guid=_devices[_destination_index].get_device_guid()
				)
				_transmissions.append(_transmission)
			_dequeue_client = _database.insert_client(
				ip_address="127.0.1.1"
			)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="735282F3-16E9-4CB0-A24E-443A72884B1E",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)
			for _transmission_index in range(len(_transmissions)):
				_transmission_dequeue = _database.get_next_transmission_dequeue(
					dequeuer_guid=_dequeuer.get_dequeuer_guid(),
					queue_guid=_queue.get_queue_guid(),
					client_guid=_dequeue_client.get_client_guid()
				)
				self.assertEqual(_transmissions[_transmission_index].get_transmission_guid(), _transmission_dequeue.get_transmission_guid())
				_database.transmission_completed(
					client_guid=_dequeue_client.get_client_guid(),
					transmission_dequeue_guid=_transmission_dequeue.get_transmission_dequeue_guid()
				)

	def test_get_devices_by_purpose_0(self):
		# one valid device
		with Database() as _database:
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			_destination_device = _database.insert_device(
				device_guid="3E1AF46C-6D1E-4349-B6EC-00557DA6C47F",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63",
				socket_port=24576
			)

			_found_devices = _database.get_devices_by_purpose(
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63"
			)
			self.assertEqual(1, len(_found_devices))

	def test_get_devices_by_purpose_1(self):
		# one valid device, one invalid device
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			_source_device = _database.insert_device(
				device_guid="C65EDB87-1F38-402E-A166-90411841AA29",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7",
				socket_port=24576
			)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			_destination_device = _database.insert_device(
				device_guid="3E1AF46C-6D1E-4349-B6EC-00557DA6C47F",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63",
				socket_port=24576
			)

			_found_devices = _database.get_devices_by_purpose(
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63"
			)
			self.assertEqual(1, len(_found_devices))

	def test_get_devices_by_purpose_2(self):
		# multiple valid and invalid devices
		_valid_purpose_guid = str(uuid.uuid4())
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			for _index in range(10):
				if _index % 2 == 0:
					_purpose_guid = _valid_purpose_guid
				else:
					_purpose_guid = str(uuid.uuid4())
				_device = _database.insert_device(
					device_guid=str(uuid.uuid4()),
					client_guid=_client.get_client_guid(),
					purpose_guid=_purpose_guid,
					socket_port=24576
				)

			_found_devices = _database.get_devices_by_purpose(
				purpose_guid=_valid_purpose_guid
			)
			self.assertEqual(5, len(_found_devices))

	def test_get_devices_by_purpose_3(self):
		# all invalid devices
		_valid_purpose_guid = str(uuid.uuid4())
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			for _index in range(10):
				_purpose_guid = str(uuid.uuid4())
				_device = _database.insert_device(
					device_guid=str(uuid.uuid4()),
					client_guid=_client.get_client_guid(),
					purpose_guid=_purpose_guid,
					socket_port=24576
				)

			_found_devices = _database.get_devices_by_purpose(
				purpose_guid=_valid_purpose_guid
			)
			self.assertEqual(0, len(_found_devices))

	def test_fail_multiple_times_0(self):
		# first transmission fails to reach destination until finally able to pull second transmission
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			_source_device = _database.insert_device(
				device_guid="C65EDB87-1F38-402E-A166-90411841AA29",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7",
				socket_port=24576
			)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			_destination_device = _database.insert_device(
				device_guid="3E1AF46C-6D1E-4349-B6EC-00557DA6C47F",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63",
				socket_port=24576
			)

			_queue = _database.insert_queue(
				queue_guid="DA970F61-77D6-4FB9-BDAA-4D24A902DD90"
			)

			_first_transmission = _database.insert_transmission(
				queue_guid="DA970F61-77D6-4FB9-BDAA-4D24A902DD90",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"first\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)

			_second_transmission = _database.insert_transmission(
				queue_guid="DA970F61-77D6-4FB9-BDAA-4D24A902DD90",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"first\": false }",
				destination_device_guid=_destination_device.get_device_guid()
			)

			_dequeue_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="E27BE734-F26C-409F-A598-160342452FA1",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)

			_failure_dequeue_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="829F8BD5-5A2A-4502-8DAB-6FBAB7F05C6F",
				is_informed_of_enqueue=False,
				client_guid=_failure_dequeue_client.get_client_guid()
			)

			for _index in range(10):
				_transmission_dequeue = _database.get_next_transmission_dequeue(
					dequeuer_guid=_dequeuer.get_dequeuer_guid(),
					queue_guid=_queue.get_queue_guid(),
					client_guid=_dequeue_client.get_client_guid()
				)
				self.assertEqual(_first_transmission.get_transmission_guid(), _transmission_dequeue.get_transmission_guid())
				_database.transmission_failed(
					client_guid=_dequeue_client.get_client_guid(),
					transmission_dequeue_guid=_transmission_dequeue.get_transmission_dequeue_guid(),
					error_message_json_string=f"{{ \"failure_index\": {_index} }}"
				)

				_failure_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
					reporter_guid=_reporter.get_reporter_guid(),
					queue_guid=_queue.get_queue_guid(),
					client_guid=_failure_dequeue_client.get_client_guid()
				)
				_database.failed_transmission_completed(
					client_guid=_failure_dequeue_client.get_client_guid(),
					transmission_dequeue_error_transmission_dequeue_guid=_failure_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
					is_retry_requested=True
				)
				_connected_device = _database.insert_device(
					device_guid="3E1AF46C-6D1E-4349-B6EC-00557DA6C47F",
					client_guid=_destination_client.get_client_guid(),
					purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63",
					socket_port=24576
				)
			_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertEqual(_first_transmission.get_transmission_guid(), _transmission_dequeue.get_transmission_guid())
			_database.transmission_completed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_transmission_dequeue.get_transmission_dequeue_guid()
			)

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_transmission_dequeue.get_transmission_guid())
			_database.transmission_completed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_second_transmission_dequeue.get_transmission_dequeue_guid()
			)

			_empty_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNone(_empty_transmission_dequeue)

	def test_failed_transmission_failed_0(self):
		# failed transmission failed and then able to send to client
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			_source_device = _database.insert_device(
				device_guid="C65EDB87-1F38-402E-A166-90411841AA29",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7",
				socket_port=24576
			)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			_destination_device = _database.insert_device(
				device_guid="3E1AF46C-6D1E-4349-B6EC-00557DA6C47F",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63",
				socket_port=24576
			)

			_queue = _database.insert_queue(
				queue_guid="D6809C07-A05B-4233-B8CA-6D033B56BC30"
			)

			_transmission = _database.insert_transmission(
				queue_guid="D6809C07-A05B-4233-B8CA-6D033B56BC30",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"first\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)

			_get_next_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="3CF492A0-AEFA-4916-9E20-9925268A5D53",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)

			_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)

			_database.transmission_failed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": true }"
			)

			_failure_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="82615F5D-E860-4686-9A70-230B2E7F0D7D",
				is_informed_of_enqueue=False,
				client_guid=_failure_client.get_client_guid()
			)

			_failure_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_client.get_client_guid()
			)

			_database.failed_transmission_failed(
				client_guid=_failure_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failure_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"failed to find source device\" }"
			)

			_empty_failure_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_client.get_client_guid()
			)
			self.assertIsNone(_empty_failure_dequeue)

			_reconnect_source_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			_reconnect_source_device = _database.insert_device(
				device_guid="C65EDB87-1F38-402E-A166-90411841AA29",
				client_guid=_reconnect_source_client.get_client_guid(),
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7",
				socket_port=24576
			)

			_retry_failure_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_client.get_client_guid()
			)
			self.assertIsNotNone(_retry_failure_dequeue)
			self.assertEqual(_retry_failure_dequeue.get_transmission_dequeue_error_transmission_guid(), _failure_dequeue.get_transmission_dequeue_error_transmission_guid())

			_database.failed_transmission_failed(
				client_guid=_failure_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_retry_failure_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				error_message_json_string="{ \"again\": true }"
			)

	def test_failed_transmission_failed_1(self):
		# failed transmission failed and then attempt to pull transmission again as if ready for retry
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			_source_device = _database.insert_device(
				device_guid="C65EDB87-1F38-402E-A166-90411841AA29",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7",
				socket_port=24576
			)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			_destination_device = _database.insert_device(
				device_guid="3E1AF46C-6D1E-4349-B6EC-00557DA6C47F",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63",
				socket_port=24576
			)

			_queue = _database.insert_queue(
				queue_guid="D6809C07-A05B-4233-B8CA-6D033B56BC30"
			)

			_transmission = _database.insert_transmission(
				queue_guid="D6809C07-A05B-4233-B8CA-6D033B56BC30",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"first\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)

			_get_next_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="3CF492A0-AEFA-4916-9E20-9925268A5D53",
				is_informed_of_enqueue=False,
				client_guid=_get_next_client.get_client_guid()
			)

			_first_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)

			_database.transmission_failed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_first_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": true }"
			)

			_failure_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="82615F5D-E860-4686-9A70-230B2E7F0D7D",
				is_informed_of_enqueue=False,
				client_guid=_failure_client.get_client_guid()
			)

			_failure_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_client.get_client_guid()
			)

			_database.failed_transmission_failed(
				client_guid=_failure_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failure_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"failed to find source device\" }"
			)

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_get_next_client.get_client_guid()
			)

			self.assertIsNone(_second_transmission_dequeue)

	def test_multiple_failed_transmissions_back_to_source_0(self):
		# source sends two transmissions to different devices and both fail and are returned to source
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			_source_device = _database.insert_device(
				device_guid="C65EDB87-1F38-402E-A166-90411841AA29",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7",
				socket_port=24576
			)
			_first_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			_first_destination_device = _database.insert_device(
				device_guid="3E1AF46C-6D1E-4349-B6EC-00557DA6C47F",
				client_guid=_first_destination_client.get_client_guid(),
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63",
				socket_port=24576
			)
			_second_destination_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			_second_destination_device = _database.insert_device(
				device_guid="0FC3A82A-7225-4BFA-B5E8-F3066E752839",
				client_guid=_second_destination_client.get_client_guid(),
				purpose_guid="7EAC6F9D-3958-4DF4-9577-BFEB8C4106F8",
				socket_port=24576
			)

			_queue = _database.insert_queue(
				queue_guid="DE7CDD8E-AE8F-49D2-BE94-2D19C4BCBF4A"
			)

			_first_transmission = _database.insert_transmission(
				queue_guid="DE7CDD8E-AE8F-49D2-BE94-2D19C4BCBF4A",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"test\": \"first\" }",
				destination_device_guid=_first_destination_device.get_device_guid()
			)

			_second_transmission = _database.insert_transmission(
				queue_guid="DE7CDD8E-AE8F-49D2-BE94-2D19C4BCBF4A",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"test\": \"second\" }",
				destination_device_guid=_second_destination_device.get_device_guid()
			)

			_dequeue_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="0A2E9940-C338-427F-804D-5DB4E2A1EC2B",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)

			_first_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_transmission_dequeue.get_transmission_guid())

			_database.transmission_failed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_first_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ }"
			)

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_transmission_dequeue.get_transmission_guid())

			_database.transmission_failed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_second_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string=None
			)

			_failure_dequeue_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="9CBFF852-247C-49E6-854A-CB649A42ED79",
				is_informed_of_enqueue=False,
				client_guid=_failure_dequeue_client.get_client_guid()
			)

			_first_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_dequeue_client.get_client_guid(),
			)
			self.assertIsNotNone(_first_failed_transmission_dequeue)
			self.assertEqual(_first_transmission_dequeue.get_transmission_dequeue_guid(), _first_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid())

			_second_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_second_failed_transmission_dequeue)
			self.assertEqual(_first_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(), _second_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid())

			_database.failed_transmission_completed(
				client_guid=_failure_dequeue_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_first_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=False
			)

			_second_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_second_failed_transmission_dequeue)
			self.assertEqual(_second_transmission_dequeue.get_transmission_dequeue_guid(), _second_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid())

	def test_multiple_failed_transmissions_back_to_source_1(self):
		# source sends two transmissions to different devices and both fail and are returned to source but source fails at first
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			_source_device = _database.insert_device(
				device_guid="C65EDB87-1F38-402E-A166-90411841AA29",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7",
				socket_port=24576
			)
			_first_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			_first_destination_device = _database.insert_device(
				device_guid="3E1AF46C-6D1E-4349-B6EC-00557DA6C47F",
				client_guid=_first_destination_client.get_client_guid(),
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63",
				socket_port=24576
			)
			_second_destination_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			_second_destination_device = _database.insert_device(
				device_guid="0FC3A82A-7225-4BFA-B5E8-F3066E752839",
				client_guid=_second_destination_client.get_client_guid(),
				purpose_guid="7EAC6F9D-3958-4DF4-9577-BFEB8C4106F8",
				socket_port=24576
			)

			_queue = _database.insert_queue(
				queue_guid="64A37BD2-FCD4-4D0F-ADD3-9263FD5316FE"
			)

			_first_transmission = _database.insert_transmission(
				queue_guid="64A37BD2-FCD4-4D0F-ADD3-9263FD5316FE",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"test\": \"first\" }",
				destination_device_guid=_first_destination_device.get_device_guid()
			)

			_second_transmission = _database.insert_transmission(
				queue_guid="64A37BD2-FCD4-4D0F-ADD3-9263FD5316FE",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"test\": \"second\" }",
				destination_device_guid=_second_destination_device.get_device_guid()
			)

			_dequeue_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="5BB17692-26E2-4D2A-B637-15F09A01D73E",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)

			_first_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_transmission_dequeue.get_transmission_guid())

			_database.transmission_failed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_first_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ }"
			)

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_transmission_dequeue.get_transmission_guid())

			_database.transmission_failed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_second_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string=None
			)

			_failure_dequeue_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="CB779604-68FA-452C-B0B2-4A7B8578F245",
				is_informed_of_enqueue=False,
				client_guid=_failure_dequeue_client.get_client_guid()
			)

			_first_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_dequeue_client.get_client_guid(),
			)
			self.assertIsNotNone(_first_failed_transmission_dequeue)
			self.assertEqual(_first_transmission_dequeue.get_transmission_dequeue_guid(), _first_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid())

			_second_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_second_failed_transmission_dequeue)
			self.assertEqual(_first_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(), _second_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid())

			_database.failed_transmission_failed(
				client_guid=_failure_dequeue_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_first_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				error_message_json_string="{ \"some_kind\": \"of error\" }"
			)

			_second_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_dequeue_client.get_client_guid()
			)
			self.assertIsNone(_second_failed_transmission_dequeue)

			_reconnected_source_client = _database.insert_client(
				ip_address="127.0.0.6"
			)
			_reconnected_source_device = _database.insert_device(
				device_guid="C65EDB87-1F38-402E-A166-90411841AA29",
				client_guid=_reconnected_source_client.get_client_guid(),
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7",
				socket_port=24576
			)

			_first_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_first_failed_transmission_dequeue)
			self.assertEqual(_first_transmission_dequeue.get_transmission_dequeue_guid(), _first_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid())

			_database.failed_transmission_completed(
				client_guid=_failure_dequeue_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_first_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=False
			)

			_second_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_failure_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_second_failed_transmission_dequeue)
			self.assertEqual(_second_transmission_dequeue.get_transmission_dequeue_guid(), _second_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid())

	def test_dequeuer_dequeue_after_dequeue_0(self):
		# dequeuer pulls twice, returning the same transmission_dequeue
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_queue = _database.insert_queue(
				queue_guid="E7FCC183-D1B4-4F3B-9BE7-A54CF25FA78F"
			)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_transmission = _database.insert_transmission(
				queue_guid="E7FCC183-D1B4-4F3B-9BE7-A54CF25FA78F",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_dequeue_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="136B7D8A-573E-45D3-B075-567ADBFE1DDE",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)
			_first_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_first_transmission_dequeue)
			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_second_transmission_dequeue)
			self.assertEqual(_first_transmission_dequeue.get_transmission_dequeue_guid(), _second_transmission_dequeue.get_transmission_dequeue_guid())

	def test_dequeuer_unresponsive_0(self):
		# dequeuer pulls transmission dequeue, completes transmission, marked unresponsive, and reconnects
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_queue = _database.insert_queue(
				queue_guid="1FEB47E3-FC20-4CCE-B346-ED1E42CA506A"
			)
			self.assertEqual("1FEB47E3-FC20-4CCE-B346-ED1E42CA506A", _queue.get_queue_guid())
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_transmission = _database.insert_transmission(
				queue_guid=_queue.get_queue_guid(),
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_dequeue_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="136B7D8A-573E-45D3-B075-567ADBFE1DDE",
				is_informed_of_enqueue=True,
				client_guid=_dequeue_client.get_client_guid()
			)
			_first_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_first_transmission_dequeue)
			_database.transmission_completed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_first_transmission_dequeue.get_transmission_dequeue_guid()
			)
			_first_responsive_dequeuers = _database.get_all_responsive_dequeuers()
			self.assertEqual(1, len(_first_responsive_dequeuers))
			_database.set_dequeuer_unresponsive(
				dequeuer_guid="136B7D8A-573E-45D3-B075-567ADBFE1DDE"
			)
			_second_responsive_dequeuers = _database.get_all_responsive_dequeuers()
			self.assertEqual(0, len(_second_responsive_dequeuers))
			_same_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="136B7D8A-573E-45D3-B075-567ADBFE1DDE",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)
			_third_responsive_dequeuers = _database.get_all_responsive_dequeuers()
			self.assertEqual(1, len(_third_responsive_dequeuers))

	def test_reporter_unresponsive_0(self):
		# dequeuer pulls transmission dequeue, fails transmission, reporter pulls failed transmission, reporter completes, marked unresponsive, and reconnects
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="66053259-5456-455A-8898-E5F708F07C27"
			)
			_transmission = _database.insert_transmission(
				queue_guid="66053259-5456-455A-8898-E5F708F07C27",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_dequeue_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="136B7D8A-573E-45D3-B075-567ADBFE1DDE",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)
			_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_transmission_dequeue)
			_database.transmission_failed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"full\": \"empty\" }"
			)
			_reporter_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="297E5526-EF3F-4506-A431-C6854CD66FA8",
				is_informed_of_enqueue=True,
				client_guid=_reporter_client.get_client_guid()
			)
			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_queue.get_queue_guid(),
				client_guid=_reporter_client.get_client_guid()
			)
			_database.failed_transmission_completed(
				client_guid=_reporter_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=False
			)
			_first_responsive_reporters = _database.get_all_responsive_reporters()
			self.assertEqual(1, len(_first_responsive_reporters))
			_database.set_reporter_unresponsive(
				reporter_guid="297E5526-EF3F-4506-A431-C6854CD66FA8"
			)
			_second_responsive_reporters = _database.get_all_responsive_reporters()
			self.assertEqual(0, len(_second_responsive_reporters))
			_same_reporter = _database.insert_reporter(
				reporter_guid="297E5526-EF3F-4506-A431-C6854CD66FA8",
				is_informed_of_enqueue=False,
				client_guid=_reporter_client.get_client_guid()
			)
			_third_responsive_reporters = _database.get_all_responsive_reporters()
			self.assertEqual(1, len(_third_responsive_reporters))

	def test_reporter_unresponsive_1(self):
		# reporter guid exists
		with Database() as _database:
			_queue = _database.insert_queue(
				queue_guid="9ACAD1F6-C27C-4E30-994B-2CFFFB02FA62"
			)
			_reporter_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="297E5526-EF3F-4506-A431-C6854CD66FA8",
				is_informed_of_enqueue=False,
				client_guid=_reporter_client.get_client_guid()
			)
			_database.set_reporter_unresponsive(
				reporter_guid="297E5526-EF3F-4506-A431-C6854CD66FA8"
			)

	def todo_reporter_unresponsive_2(self):  # TODO
		# reporter guid not exists
		with Database() as _database:
			_reporter_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="297E5526-EF3F-4506-A431-C6854CD66FA8",
				is_informed_of_enqueue=False,
				client_guid=_reporter_client.get_client_guid()
			)
			with self.assertRaises(NotImplementedError):
				_database.set_reporter_unresponsive(
					reporter_guid="1CEBE505-4DC3-4885-8C9D-8862CEC771B7"
				)

	def test_api_entrypoint_log_0(self):
		# insert each type of api entrypoint
		with Database() as _database:
			_client = _database.insert_client(
				ip_address="127.0.0.1"
			)

			_start_datetime = datetime.utcnow()

			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.TestGet,
				input_json_string=None
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1ReceiveDeviceAnnouncement,
				input_json_string=""
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1ReceiveDeviceTransmission,
				input_json_string="{ }"
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1DequeueNextTransmission,
				input_json_string="{ \"test\": true }"
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1CompleteTransmission,
				input_json_string="{ \"transmission_dequeue_guid\": \"7F496997-57D1-4803-8DD5-57ECFC858DE9\" }"
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1FailedTransmission,
				input_json_string="{ \"first\": 1, \"second\": 2 }"
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1DequeueFailureTransmission,
				input_json_string=f"{{ \"size_test\": \"{'1234567890' * 10**5}\" }}"
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1CompleteFailureTransmission,
				input_json_string=f"{{ \"size_test\": \"{'1234567890' * 10**6}\" }}"
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1FailedFailureTransmission,
				input_json_string=f"{{ \"size_test\": \"{'1234567890' * 10**7}\" }}"
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1ReceiveDequeuerAnnouncement,
				input_json_string=None
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1ReceiveReporterAnnouncement,
				input_json_string=None
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1DequeueFailureTransmission,
				input_json_string=None
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.V1GetUuid,
				input_json_string=None
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.TestPost,
				input_json_string=None
			)
			_database.insert_api_entrypoint_log(
				client_guid=_client.get_client_guid(),
				api_entrypoint=ApiEntrypoint.TestJson,
				input_json_string=None
			)

			_end_datetime = datetime.utcnow()

			_api_entrypoint_logs = _database.get_api_entrypoint_logs(
				inclusive_start_row_created_datetime=_start_datetime,
				exclusive_end_row_created_datetime=_end_datetime
			)

			self.assertEqual(len(ApiEntrypoint), len(_api_entrypoint_logs))
			self.assertEqual(None, _api_entrypoint_logs[0].get_input_json_string())
			self.assertEqual("", _api_entrypoint_logs[1].get_input_json_string())
			self.assertEqual("{ }", _api_entrypoint_logs[2].get_input_json_string())
			self.assertEqual("{ \"test\": true }", _api_entrypoint_logs[3].get_input_json_string())
			self.assertEqual("{ \"transmission_dequeue_guid\": \"7F496997-57D1-4803-8DD5-57ECFC858DE9\" }", _api_entrypoint_logs[4].get_input_json_string())
			self.assertEqual("{ \"first\": 1, \"second\": 2 }", _api_entrypoint_logs[5].get_input_json_string())
			self.assertEqual(f"{{ \"size_test\": \"{'1234567890' * 10**5}\" }}", _api_entrypoint_logs[6].get_input_json_string())
			self.assertEqual(f"{{ \"size_test\": \"{'1234567890' * 10**6}\" }}", _api_entrypoint_logs[7].get_input_json_string())
			self.assertEqual(f"{{ \"size_test\": \"{'1234567890' * 10**7}\" }}", _api_entrypoint_logs[8].get_input_json_string())

	def test_different_queues_0(self):
		# insert transmission into different queue, dequeuer fails to find transmission
		with Database() as _database:
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_queue = _database.insert_queue(
				queue_guid="66053259-5456-455A-8898-E5F708F07C27"
			)
			_transmission = _database.insert_transmission(
				queue_guid="66053259-5456-455A-8898-E5F708F07C27",
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_transmission)
			_dequeue_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_dequeuer_queue = _database.insert_queue(
				queue_guid="CE50E40E-D888-4684-B72C-654FCF81975F",
			)
			_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="136B7D8A-573E-45D3-B075-567ADBFE1DDE",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)
			_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_dequeuer.get_dequeuer_guid(),
				queue_guid="CE50E40E-D888-4684-B72C-654FCF81975F",
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNone(_transmission_dequeue)

	def test_different_queues_1(self):
		# dequeuer queue changes
		with Database() as _database:
			_first_queue = _database.insert_queue(
				queue_guid="66053259-5456-455A-8898-E5F708F07C27"
			)
			_second_queue = _database.insert_queue(
				queue_guid="CE50E40E-D888-4684-B72C-654FCF81975F",
			)
			_dequeue_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_first_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="136B7D8A-573E-45D3-B075-567ADBFE1DDE",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)
			_second_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="136B7D8A-573E-45D3-B075-567ADBFE1DDE",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertEqual(_first_dequeuer.get_dequeuer_guid(), _second_dequeuer.get_dequeuer_guid())

	def test_different_queues_2(self):
		# insert transmission into different queue, two transmissions and two dequeuers and two reporters, same source and destination so second dequeuer must wait for earlier transmission for first dequeuer
		with Database() as _database:
			_first_queue = _database.insert_queue(
				queue_guid="66053259-5456-455A-8898-E5F708F07C27"
			)
			_second_queue = _database.insert_queue(
				queue_guid="CE50E40E-D888-4684-B72C-654FCF81975F",
			)
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_first_transmission = _database.insert_transmission(
				queue_guid=_first_queue.get_queue_guid(),
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_second_transmission = _database.insert_transmission(
				queue_guid=_second_queue.get_queue_guid(),
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": false }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_second_transmission)
			_dequeue_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_first_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="136B7D8A-573E-45D3-B075-567ADBFE1DDE",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)
			_second_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="22E4B5F4-4DDF-421D-B160-70D2F8120E5B",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)

			# second dequeuer must wait for the earlier transmission for this destination

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_second_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNone(_second_transmission_dequeue)

			# first dequeuer must occur prior to second dequeuer

			_first_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_first_dequeuer.get_dequeuer_guid(),
				queue_guid=_first_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_first_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_transmission_dequeue.get_transmission_guid())

			# trying to call the second dequeuer should still fail because the first transmission is not in a completed state

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_second_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNone(_second_transmission_dequeue)

			# failing the transmission should not unblock the second dequeuer

			_database.transmission_failed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_first_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"message\": \"testing entire process blocks second transmission\" }"
			)

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_second_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNone(_second_transmission_dequeue)

			# pulling the failed transmission should not unblock the second dequeuer

			_reporter_client = _database.insert_client(
				ip_address="127.0.1.0"
			)
			_reporter = _database.insert_reporter(
				reporter_guid="DAB74CDA-4690-40B1-ABBB-54C601E6EBA1",
				is_informed_of_enqueue=False,
				client_guid=_reporter_client.get_client_guid()
			)

			_first_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_reporter.get_reporter_guid(),
				queue_guid=_first_queue.get_queue_guid(),
				client_guid=_reporter_client.get_client_guid()
			)
			self.assertIsNotNone(_first_failed_transmission_dequeue)

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_second_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNone(_second_transmission_dequeue)

			# setting the failed transmission to retry should not unblock the second transmission

			_database.failed_transmission_completed(
				client_guid=_reporter_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_first_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=True
			)

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_second_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNone(_second_transmission_dequeue)

			# the first transaction cannot be immediately pulled without the destination reconnecting

			_first_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_first_dequeuer.get_dequeuer_guid(),
				queue_guid=_first_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNone(_first_transmission_dequeue)

			_destination_device = _database.insert_device(
				device_guid=_destination_device.get_device_guid(),
				client_guid=_destination_client.get_client_guid(),
				purpose_guid=_destination_device.get_purpose_guid(),
				socket_port=24576
			)

			# pulling the transaction again should not unblock the second transaction

			_first_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_first_dequeuer.get_dequeuer_guid(),
				queue_guid=_first_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_first_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_transmission_dequeue.get_transmission_guid())

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_second_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNone(_second_transmission_dequeue)

			# closing the first transaction should unblock the second transaction

			_database.transmission_completed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_first_transmission_dequeue.get_transmission_dequeue_guid()
			)

			# now the second dequeuer should succeed

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_second_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_second_transmission_dequeue)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_transmission_dequeue.get_transmission_guid())

	def test_different_queues_3(self):
		# insert transmission into different queue, two transmissions and two dequeuers and two reporters, same source but different destination
		with Database() as _database:
			_first_queue = _database.insert_queue(
				queue_guid="66053259-5456-455A-8898-E5F708F07C27"
			)
			_second_queue = _database.insert_queue(
				queue_guid="CE50E40E-D888-4684-B72C-654FCF81975F",
			)
			_source_client = _database.insert_client(
				ip_address="127.0.0.1"
			)
			self.assertIsNotNone(_source_client)
			_source_device = _database.insert_device(
				device_guid="6B9C16F6-56B2-495F-9D89-98415C71EB7E",
				client_guid=_source_client.get_client_guid(),
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D",
				socket_port=24576
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_first_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_first_destination_device)
			_second_destination_device = _database.insert_device(
				device_guid="7B0C7428-AD10-4E0E-BB5E-6B38CF9AB7BA",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5",
				socket_port=24576
			)
			self.assertIsNotNone(_second_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_first_transmission = _database.insert_transmission(
				queue_guid=_first_queue.get_queue_guid(),
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_first_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_second_transmission = _database.insert_transmission(
				queue_guid=_second_queue.get_queue_guid(),
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": false }",
				destination_device_guid=_second_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_second_transmission)
			_dequeue_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			_first_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="136B7D8A-573E-45D3-B075-567ADBFE1DDE",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)
			_second_dequeuer = _database.insert_dequeuer(
				dequeuer_guid="22E4B5F4-4DDF-421D-B160-70D2F8120E5B",
				is_informed_of_enqueue=False,
				client_guid=_dequeue_client.get_client_guid()
			)

			# attempting to pull second transmission should be fine since it's a different destination than the earlier/first transmission

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_second_dequeuer.get_dequeuer_guid(),
				queue_guid=_second_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_second_transmission_dequeue)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_transmission_dequeue.get_transmission_guid())

			# the first transmission can be pulled prior to the second transmission being completed

			_first_transmission_dequeue = _database.get_next_transmission_dequeue(
				dequeuer_guid=_first_dequeuer.get_dequeuer_guid(),
				queue_guid=_first_queue.get_queue_guid(),
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_first_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_transmission_dequeue.get_transmission_guid())

			# the failed transmissions can only be pulled once the source has sequentially dealt with the responses

			_database.transmission_failed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_second_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"order\": \"first\" }"
			)

			_database.transmission_failed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_first_transmission_dequeue.get_transmission_dequeue_guid(),
				error_message_json_string="{ \"order\": \"second\" }"
			)

			_reporter_client = _database.insert_client(
				ip_address="127.0.2.0"
			)
			_first_reporter = _database.insert_reporter(
				reporter_guid="A0CF5891-6BA5-4962-A6BB-C46BF11990C2",
				is_informed_of_enqueue=False,
				client_guid=_reporter_client.get_client_guid()
			)
			_second_reporter = _database.insert_reporter(
				reporter_guid="CC3B6496-D92D-47A7-BBC2-841B007A6326",
				is_informed_of_enqueue=False,
				client_guid=_reporter_client.get_client_guid()
			)

			_second_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_second_reporter.get_reporter_guid(),
				queue_guid=_second_queue.get_queue_guid(),
				client_guid=_reporter_client.get_client_guid()
			)
			self.assertIsNotNone(_second_failed_transmission_dequeue)
			self.assertEqual(_second_transmission_dequeue.get_transmission_dequeue_guid(), _second_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid())

			_first_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_first_reporter.get_reporter_guid(),
				queue_guid=_first_queue.get_queue_guid(),
				client_guid=_reporter_client.get_client_guid()
			)
			self.assertIsNone(_first_failed_transmission_dequeue)

			# with the second failed transmission dequeue responded to, the first failed transmission dequeue can finally be pulled and sent to the source

			_database.failed_transmission_completed(
				client_guid=_reporter_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_second_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=True
			)

			_first_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				reporter_guid=_first_reporter.get_reporter_guid(),
				queue_guid=_first_queue.get_queue_guid(),
				client_guid=_reporter_client.get_client_guid()
			)
			self.assertIsNotNone(_first_failed_transmission_dequeue)
			self.assertEqual(_first_transmission_dequeue.get_transmission_dequeue_guid(), _first_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid())


if __name__ == "__main__":
	unittest.main()
