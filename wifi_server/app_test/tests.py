from __future__ import annotations
from app.database import Database, Client, Device, Transmission
import unittest
import sqlite3
from typing import List, Tuple, Dict
import uuid


class DatabaseTest(unittest.TestCase):

	def test_insert_device_0(self):
		# missing client
		with Database() as _database:
			_device = None
			with self.assertRaises(sqlite3.IntegrityError):
				_device = _database.insert_device(
					device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
					client_guid="8D825258-C1A3-43AF-A354-6C2EA7561F53",
					purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
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
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
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
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
			)
			self.assertIsNotNone(_device)
			_other_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
			)
			self.assertIsNotNone(_other_device)
			self.assertEqual(_device.get_device_guid(), _other_device.get_device_guid())
			self.assertEqual(_device.get_purpose_guid(), _other_device.get_purpose_guid())
			self.assertEqual(_device.to_json(), _other_device.to_json())
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
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
			)
			self.assertIsNotNone(_device)
			_other_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_client.get_client_guid(),
				purpose_guid="C439928B-A339-4550-8E2D-B5583C90FD40"
			)
			self.assertIsNotNone(_other_device)
			self.assertEqual(_device.get_device_guid(), _other_device.get_device_guid())
			self.assertNotEqual(_device.get_purpose_guid(), _other_device.get_purpose_guid())
			self.assertNotEqual(_device.to_json(), _other_device.to_json())
			_database_device = _database.get_device(
				device_guid=_device.get_device_guid()
			)
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
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
			)
			self.assertIsNotNone(_device)
			_other_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_other_client)
			_other_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_other_client.get_client_guid(),
				purpose_guid="C439928B-A339-4550-8E2D-B5583C90FD40"
			)
			self.assertIsNotNone(_other_device)
			self.assertEqual(_device.get_device_guid(), _other_device.get_device_guid())
			self.assertNotEqual(_device.get_purpose_guid(), _other_device.get_purpose_guid())
			self.assertNotEqual(_device.to_json(), _other_device.to_json())
			_database_device = _database.get_device(
				device_guid=_device.get_device_guid()
			)
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
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
			)
			self.assertIsNotNone(_device)
			_other_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_other_client)
			_other_device = _database.insert_device(
				device_guid="1202BF8A-D185-4C32-8931-C4315B0B87D9",
				client_guid=_other_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
			)
			self.assertIsNotNone(_other_device)
			self.assertEqual(_device.get_device_guid(), _other_device.get_device_guid())
			self.assertEqual(_device.get_purpose_guid(), _other_device.get_purpose_guid())
			self.assertEqual(_device.to_json(), _other_device.to_json())
			_database_device = _database.get_device(
				device_guid=_device.get_device_guid()
			)
			self.assertEqual(_device.get_device_guid(), _database_device.get_device_guid())
			self.assertEqual(_device.get_purpose_guid(), _database_device.get_purpose_guid())
			self.assertEqual(_other_device.get_purpose_guid(), _database_device.get_purpose_guid())
			self.assertEqual(_device.to_json(), _database_device.to_json())
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
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
			)
			self.assertIsNotNone(_device)
			_other_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_other_client)
			_other_device = _database.insert_device(
				device_guid="B3D1577E-2874-4F0C-AFD7-254DB00F47CF",
				client_guid=_other_client.get_client_guid(),
				purpose_guid="B978714F-B6EB-4E6B-83EB-2BD9C702F753"
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
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
			)
			self.assertIsNotNone(_device)
			_other_device = _database.insert_device(
				device_guid="B3D1577E-2874-4F0C-AFD7-254DB00F47CF",
				client_guid=_client.get_client_guid(),
				purpose_guid="B978714F-B6EB-4E6B-83EB-2BD9C702F753"
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
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
			)
			self.assertIsNotNone(_device)
			_other_device = _database.insert_device(
				device_guid="B3D1577E-2874-4F0C-AFD7-254DB00F47CF",
				client_guid=_client.get_client_guid(),
				purpose_guid="27C61F73-9436-4416-AD48-7329B899C212"
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
			with self.assertRaises(sqlite3.IntegrityError):
				_transmission = _database.insert_transmission(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_transmission = _database.insert_transmission(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_transmission = _database.insert_transmission(
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
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_first_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_second_transmission = _database.insert_transmission(
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
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_first_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_second_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"other\": 1 }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_second_transmission)
			_get_next_client_first = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client_first)
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				client_guid=_get_next_client_first.get_client_guid()
			)
			self.assertIsNotNone(_first_get_next_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_get_next_transmission_dequeue.get_transmission_guid())
			_get_next_client_second = _database.insert_client(
				ip_address="127.0.0.5"
			)
			self.assertIsNotNone(_get_next_client_second)

			# transmission completed

			_database.transmission_completed(
				client_guid=_get_next_client_first.get_client_guid(),
				transmission_dequeue_guid=_first_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

			# dequeue second transmission

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				client_guid=_get_next_client_second.get_client_guid()
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_first_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_second_transmission = _database.insert_transmission(
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
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_get_next_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_get_next_transmission_dequeue.get_transmission_guid())

			# dequeue second transmission

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNone(_second_get_next_transmission_dequeue)

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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_transmission = _database.insert_transmission(
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
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_transmission = _database.insert_transmission(
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
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_transmission = _database.insert_transmission(
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
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_first_transmission = _database.insert_transmission(
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
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"second\": \"transmission\" }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_first_transmission = _database.insert_transmission(
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
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_first_get_next_transmission_dequeue)
			self.assertEqual(_first_transmission.get_transmission_guid(), _first_get_next_transmission_dequeue.get_transmission_guid())
			_second_transmission = _database.insert_transmission(
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
			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				client_guid=_failed_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)

			_database.failed_transmission_completed(
				client_guid=_failed_dequeue_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=False
			)

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_first_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_transmission_client.get_client_guid(),
				transmission_json_string="{ \"test\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_first_transmission)
			_second_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"second\": \"transmission\" }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			_get_next_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			self.assertIsNotNone(_get_next_client)
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				client_guid=_failed_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)

			_database.failed_transmission_completed(
				client_guid=_failed_dequeue_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=False
			)

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_first_transmission = _database.insert_transmission(
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
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				client_guid=_failed_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)

			_database.failed_transmission_completed(
				client_guid=_failed_dequeue_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=False
			)

			_second_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"second\": \"transmission\" }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_first_transmission = _database.insert_transmission(
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
			_first_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				client_guid=_failed_dequeue_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)

			_database.failed_transmission_completed(
				client_guid=_failed_dequeue_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failed_transmission_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				is_retry_requested=True
			)

			_second_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"second\": \"transmission\" }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_transmission = _database.insert_transmission(
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
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
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
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertEqual(_destination_device.get_device_guid(), _same_device.get_device_guid())
			self.assertEqual(_destination_device.get_purpose_guid(), _same_device.get_purpose_guid())
			self.assertEqual(_destination_device.to_json(), _same_device.to_json())

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_transmission = _database.insert_transmission(
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
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
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
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertEqual(_destination_device.get_device_guid(), _same_device.get_device_guid())
			self.assertEqual(_destination_device.get_purpose_guid(), _same_device.get_purpose_guid())
			self.assertEqual(_destination_device.to_json(), _same_device.to_json())

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="6EABEE26-24C2-4698-8BBA-8707E0397C7D"
			)
			self.assertIsNotNone(_source_device)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			self.assertIsNotNone(_destination_client)
			_destination_device = _database.insert_device(
				device_guid="2D2EA5D3-95E3-4B71-AE7A-DDD0ED5AA40B",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertIsNotNone(_destination_device)
			_transmission_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			self.assertIsNotNone(_transmission_client)
			_transmission = _database.insert_transmission(
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
			_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				client_guid=_failed_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)
			self.assertEqual(_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid(), _get_next_transmission_dequeue.get_transmission_dequeue_guid())

			# another transmission is queued up before the failed transmission is sent back to the origin

			_second_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"after_failure\": \"yup\" }",
				destination_device_guid=_destination_device.get_device_guid()
			)
			self.assertIsNotNone(_second_transmission)

			# dequeuing the second transmission should fail because the destination has a failed transmission

			_first_attempt_second_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="330A6549-57C5-4DA6-8C1C-A698A61B7DB5"
			)
			self.assertEqual(_destination_device.get_device_guid(), _same_device.get_device_guid())
			self.assertEqual(_destination_device.get_purpose_guid(), _same_device.get_purpose_guid())
			self.assertEqual(_destination_device.to_json(), _same_device.to_json())

			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
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
					purpose_guid=str(uuid.uuid4())
				)
				_clients.append(_client)
				_devices.append(_device)
			_transmissions = []  # type: List[Transmission]
			for _index in range(len(_devices)**2):
				_source_index = _index % len(_devices)
				_destination_index = (_index + 1) % len(_devices)
				_transmission = _database.insert_transmission(
					source_device_guid=_devices[_source_index].get_device_guid(),
					client_guid=_clients[_source_index].get_client_guid(),
					transmission_json_string=f"{{ \"transmission\": {_index} }}",
					destination_device_guid=_devices[_destination_index].get_device_guid()
				)
				_transmissions.append(_transmission)
			_dequeue_client = _database.insert_client(
				ip_address="127.0.1.1"
			)
			for _transmission_index in range(len(_transmissions)):
				_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63"
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
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7"
			)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			_destination_device = _database.insert_device(
				device_guid="3E1AF46C-6D1E-4349-B6EC-00557DA6C47F",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63"
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
					purpose_guid=_purpose_guid
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
					purpose_guid=_purpose_guid
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
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7"
			)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			_destination_device = _database.insert_device(
				device_guid="3E1AF46C-6D1E-4349-B6EC-00557DA6C47F",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63"
			)

			_first_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"first\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)

			_second_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"first\": false }",
				destination_device_guid=_destination_device.get_device_guid()
			)

			_dequeue_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			_failure_dequeue_client = _database.insert_client(
				ip_address="127.0.0.4"
			)
			for _index in range(10):
				_transmission_dequeue = _database.get_next_transmission_dequeue(
					client_guid=_dequeue_client.get_client_guid()
				)
				self.assertEqual(_first_transmission.get_transmission_guid(), _transmission_dequeue.get_transmission_guid())
				_database.transmission_failed(
					client_guid=_dequeue_client.get_client_guid(),
					transmission_dequeue_guid=_transmission_dequeue.get_transmission_dequeue_guid(),
					error_message_json_string=f"{{ \"failure_index\": {_index} }}"
				)

				_failure_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
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
					purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63"
				)
			_transmission_dequeue = _database.get_next_transmission_dequeue(
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertEqual(_first_transmission.get_transmission_guid(), _transmission_dequeue.get_transmission_guid())
			_database.transmission_completed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_transmission_dequeue.get_transmission_dequeue_guid()
			)

			_second_transmission_dequeue = _database.get_next_transmission_dequeue(
				client_guid=_dequeue_client.get_client_guid()
			)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_transmission_dequeue.get_transmission_guid())
			_database.transmission_completed(
				client_guid=_dequeue_client.get_client_guid(),
				transmission_dequeue_guid=_second_transmission_dequeue.get_transmission_dequeue_guid()
			)

			_empty_transmission_dequeue = _database.get_next_transmission_dequeue(
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
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7"
			)
			_destination_client = _database.insert_client(
				ip_address="127.0.0.2"
			)
			_destination_device = _database.insert_device(
				device_guid="3E1AF46C-6D1E-4349-B6EC-00557DA6C47F",
				client_guid=_destination_client.get_client_guid(),
				purpose_guid="7B3316A1-89F4-49A0-A6B3-351CC5FE6D63"
			)

			_transmission = _database.insert_transmission(
				source_device_guid=_source_device.get_device_guid(),
				client_guid=_source_client.get_client_guid(),
				transmission_json_string="{ \"first\": true }",
				destination_device_guid=_destination_device.get_device_guid()
			)

			_get_next_client = _database.insert_client(
				ip_address="127.0.0.3"
			)
			_transmission_dequeue = _database.get_next_transmission_dequeue(
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
			_failure_dequeue = _database.get_next_failed_transmission_dequeue(
				client_guid=_failure_client.get_client_guid()
			)

			_database.failed_transmission_failed(
				client_guid=_failure_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_failure_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				error_message_json_string="{ \"error\": \"failed to find source device\" }"
			)

			_empty_failure_dequeue = _database.get_next_failed_transmission_dequeue(
				client_guid=_failure_client.get_client_guid()
			)
			self.assertIsNone(_empty_failure_dequeue)

			_reconnect_source_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			_reconnect_source_device = _database.insert_device(
				device_guid="C65EDB87-1F38-402E-A166-90411841AA29",
				client_guid=_reconnect_source_client.get_client_guid(),
				purpose_guid="06D83FD4-FE47-4257-804A-7DBD9E9359C7"
			)

			_retry_failure_dequeue = _database.get_next_failed_transmission_dequeue(
				client_guid=_failure_client.get_client_guid()
			)
			self.assertIsNotNone(_retry_failure_dequeue)
			self.assertEqual(_retry_failure_dequeue.get_transmission_dequeue_error_transmission_guid(), _failure_dequeue.get_transmission_dequeue_error_transmission_guid())

			_database.failed_transmission_failed(
				client_guid=_failure_client.get_client_guid(),
				transmission_dequeue_error_transmission_dequeue_guid=_retry_failure_dequeue.get_transmission_dequeue_error_transmission_dequeue_guid(),
				error_message_json_string="{ \"again\": true }"
			)


if __name__ == "__main__":
	unittest.main()
