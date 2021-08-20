from __future__ import annotations
from app.database import Database
import unittest
import sqlite3


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
			_get_next_transmission_dequeue_first = _database.get_next_transmission_dequeue(
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue_first)
			self.assertEqual(_first_transmission.get_transmission_guid(), _get_next_transmission_dequeue_first.get_transmission_guid())
			_get_next_transmission_dequeue_second = _database.get_next_transmission_dequeue(
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue_second)
			self.assertEqual(_second_transmission.get_transmission_guid(), _get_next_transmission_dequeue_second.get_transmission_guid())

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
			_get_next_transmission_dequeue_first = _database.get_next_transmission_dequeue(
				client_guid=_get_next_client_first.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue_first)
			self.assertEqual(_first_transmission.get_transmission_guid(), _get_next_transmission_dequeue_first.get_transmission_guid())
			_get_next_client_second = _database.insert_client(
				ip_address="127.0.0.5"
			)
			self.assertIsNotNone(_get_next_client_second)
			_get_next_transmission_dequeue_second = _database.get_next_transmission_dequeue(
				client_guid=_get_next_client_second.get_client_guid()
			)
			self.assertIsNotNone(_get_next_transmission_dequeue_second)
			self.assertEqual(_second_transmission.get_transmission_guid(), _get_next_transmission_dequeue_second.get_transmission_guid())

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
		# queue first, pull first, mark failed, queue second, pull second, mark completed
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
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_completed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_second_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

	def test_transmission_failed_2(self):
		# queue first, pull first, queue second, mark failed, pull second, mark completed
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
			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_completed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_second_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

	def test_transmission_failed_3(self):
		# queue first, queue second, pull first, mark failed, pull second, mark completed
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
			_second_get_next_transmission_dequeue = _database.get_next_transmission_dequeue(
				client_guid=_get_next_client.get_client_guid()
			)
			self.assertEqual(_second_transmission.get_transmission_guid(), _second_get_next_transmission_dequeue.get_transmission_guid())
			_database.transmission_completed(
				client_guid=_get_next_client.get_client_guid(),
				transmission_dequeue_guid=_second_get_next_transmission_dequeue.get_transmission_dequeue_guid()
			)

	def test_transmission_failed_and_transmit_0(self):
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
			_failed_client = _database.insert_client(
				ip_address="127.0.0.5"
			)
			self.assertIsNotNone(_failed_client)
			_failed_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
				client_guid=_failed_client.get_client_guid()
			)
			self.assertIsNotNone(_failed_transmission_dequeue)
			self.assertEqual(_failed_transmission_dequeue.get_transmission_dequeue_error_transmission().get_transmission_dequeue_guid(), _get_next_transmission_dequeue.get_transmission_dequeue_guid())


if __name__ == "__main__":
	unittest.main()
