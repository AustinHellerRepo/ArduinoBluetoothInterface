from __future__ import annotations
from enum import IntEnum
import sqlite3
import uuid


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

	def __init__(self, *, device_id: int, unique_id: str, purpose_id: int):

		self.__device_id = device_id
		self.__unique_id = unique_id
		self.__purpose_id = purpose_id

	def get_device_id(self) -> int:
		return self.__device_id

	def get_unique_id(self) -> str:
		return self.__unique_id

	def get_purpose_id(self) -> int:
		return self.__purpose_id

	def to_json(self) -> object:
		return {
			"database_id": self.__device_id,
			"unique_id": self.__unique_id,
			"purpose_id": self.__purpose_id
		}


class Database():

	def __init__(self):

		self.__connection = sqlite3.connect(":memory:")

		self.__initialize()

	def __initialize(self):

		_cursor = self.__connection.cursor()
		_cursor.execute("CREATE TABLE device (device_id INTEGER PRIMARY KEY AUTOINCREMENT, unique_id TEXT, purpose_id INTEGER)")
		_cursor.execute("CREATE TABLE client (client_guid GUID PRIMARY KEY, ip_address TEXT)")

	def insert_client(self, *, ip_address: str) -> Client:

		_client_guid = str(uuid.uuid4())

		_cursor = self.__connection.cursor()
		_cursor.execute("INSERT INTO client VALUES (?, ?)", (_client_guid, ip_address))

		_client = Client(
			client_guid=_client_guid,
			ip_address=ip_address
		)
		return _client

	def insert_device(self, *, unique_id: str, purpose_id: int) -> Device:

		_cursor = self.__connection.cursor()
		_cursor.execute("INSERT INTO device VALUES (?, ?, ?)", (None, unique_id, purpose_id))
		_device_id = _cursor.lastrowid

		_device = Device(
			device_id=_device_id,
			unique_id=unique_id,
			purpose_id=purpose_id
		)
		return _device
