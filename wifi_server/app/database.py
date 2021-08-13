from __future__ import annotations
from enum import IntEnum
import sqlite3
import uuid
from datetime import datetime


class Purpose(IntEnum):

	DoorLight = 1,
	DeskController = 2


class Client():

	def __init__(self, *, client_guid: str, ip_address: str):

		self.__client_guid = client_guid
		self.__ip_address = ip_address

	def get_client_guid(self) -> str:
		return self.__client_guid

	def get_ip_address(self) -> str:
		return self.__ip_address


class Device():

	def __init__(self, *, device_guid: str, purpose_id: int):

		self.__device_guid = device_guid
		self.__purpose_id = purpose_id

	def get_device_guid(self) -> str:
		return self.__device_guid

	def get_purpose_id(self) -> int:
		return self.__purpose_id

	def to_json(self) -> object:
		return {
			"device_guid": self.__device_guid,
			"purpose_id": self.__purpose_id
		}


class Transmission():

	def __init__(self, *, transmission_id: int, source_device_guid: str, source_client_guid: str, transmission_json_string: str, destination_device_guid: str, dequeue_client_guid: str, sent_guid: str):

		self.__transmission_id = transmission_id
		self.__source_device_guid = source_device_guid
		self.__source_client_guid = source_client_guid
		self.__transmission_json_string = transmission_json_string
		self.__destination_device_guid = destination_device_guid
		self.__dequeue_client_guid = dequeue_client_guid
		self.__sent_guid = sent_guid

	def get_transmission_id(self) -> int:
		return self.__transmission_id

	def get_source_device_guid(self) -> str:
		return self.__source_device_guid

	def get_source_client_guid(self) -> str:
		return self.__source_client_guid

	def get_transmission_json_string(self) -> str:
		return self.__transmission_json_string

	def get_destination_device_guid(self) -> str:
		return self.__destination_device_guid

	def get_dequeue_client_guid(self) -> str:
		return self.__dequeue_client_guid

	def get_sent_guid(self) -> str:
		return self.__sent_guid

	def to_json(self) -> object:
		return {
			"transmission_id": self.__transmission_id,
			"source_device_guid": self.__source_device_guid,
			"source_client_guid": self.__source_client_guid,
			"transmission_json_string": self.__transmission_json_string,
			"destination_device_guid": self.__destination_device_guid,
			"dequeue_client_guid": self.__dequeue_client_guid,
			"sent_guid": self.__sent_guid
		}


class Database():

	def __init__(self):

		self.__connection = sqlite3.connect(":memory:")

		self.__initialize()

	def __initialize(self):

		_cursor = self.__connection.cursor()
		_cursor.execute("CREATE TABLE device (device_guid GUID PRIMARY KEY, purpose_id INTEGER, last_known_datetime REAL, is_active INTEGER)")
		_cursor.execute("CREATE TABLE client (client_guid GUID PRIMARY KEY, ip_address TEXT, UNIQUE(ip_address))")
		_cursor.execute("CREATE TABLE transmission (transmission_id INTEGER PRIMARY KEY AUTOINCREMENT, source_device_guid GUID, source_client_guid GUID, transmission_json_string TEXT, destination_device_guid GUID, dequeue_client_guid GUID, sent_guid GUID)")

	def insert_client(self, *, ip_address: str) -> Client:

		_client_guid = str(uuid.uuid4())

		_insert_cursor = self.__connection.cursor()
		_insert_cursor.execute("INSERT OR IGNORE INTO client (client_guid, ip_address) VALUES (?, ?)", (_client_guid, ip_address))

		_get_guid_cursor = self.__connection.cursor()
		_get_guid_result = _get_guid_cursor.execute("SELECT client_guid FROM client WHERE ip_address = ?", (ip_address, ))

		_saved_guid = _get_guid_result.fetchall()[0][0]

		_client = Client(
			client_guid=_saved_guid,
			ip_address=ip_address
		)
		return _client

	def insert_device(self, *, device_guid: str, purpose_id: int) -> Device:

		_insert_cursor = self.__connection.cursor()
		_insert_cursor.execute("INSERT OR IGNORE INTO device (device_guid, purpose_id, last_known_datetime, is_active) VALUES (?, ?, ?, ?)", (device_guid, purpose_id, datetime.utcnow(), 1))

		_update_known_datetime_cursor = self.__connection.cursor()
		_update_known_datetime_cursor.execute("UPDATE device SET last_known_datetime = ? WHERE device_guid = ?", (datetime.utcnow(), device_guid))

		_device = Device(
			device_guid=device_guid,
			purpose_id=purpose_id
		)
		return _device

	def insert_transmission(self, *, source_device_guid: str, client_guid: str, transmission_json_string: str, destination_device_guid: str) -> Transmission:

		_insert_cursor = self.__connection.cursor()
		_insert_cursor.execute("INSERT INTO transmission (transmission_id, source_device_guid, source_client_guid, transmission_json_string, destination_device_guid, dequeue_client_guid, sent_guid) VALUES (?, ?, ?, ?, ?, ?, ?)", (None, source_device_guid, client_guid, transmission_json_string, destination_device_guid, None, None))
		_transmission_id = _insert_cursor.lastrowid

		_transmission = Transmission(
			transmission_id=_transmission_id,
			source_device_guid=source_device_guid,
			source_client_guid=client_guid,
			transmission_json_string=transmission_json_string,
			destination_device_guid=destination_device_guid,
			dequeue_client_guid=None,
			sent_guid=None
		)
		return _transmission

	def get_next_transmission(self, *, client_guid: str) -> Transmission:

		_sent_guid = str(uuid.uuid4())

		_update_cursor = self.__connection.cursor()
		_update_cursor.execute("UPDATE transmission SET dequeue_client_guid = ?, sent_guid = ? WHERE transmission_id = (SELECT t_inner.transmission_id FROM transmission AS t_inner WHERE t_inner.sent_guid IS NULL ORDER BY t_inner.transmission_id LIMIT 1)", (client_guid, _sent_guid))

		_get_cursor = self.__connection.cursor()
		_get_result = _get_cursor.execute("SELECT transmission_id, source_device_guid, source_client_guid, transmission_json_string, destination_device_guid FROM transmission WHERE sent_guid = ?", (_sent_guid, ))

		_rows = _get_result.fetchall()
		if len(_rows) == 0:
			_transmission = None
		else:
			_row = _rows[0]

			_transmission = Transmission(
				transmission_id=_row[0],
				source_device_guid=_row[1],
				source_client_guid=_row[2],
				transmission_json_string=_row[3],
				destination_device_guid=_row[4],
				dequeue_client_guid=client_guid,
				sent_guid=_sent_guid
			)
		return _transmission
