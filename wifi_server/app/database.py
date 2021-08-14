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

	def __init__(self, *, transmission_guid: str, source_device_guid: str, source_client_guid: str, transmission_json_string: str, destination_device_guid: str, dequeue_client_guid: str, dequeue_token_guid: str, completed_client_guid: str, row_created_datetime: datetime, dequeued_datetime: datetime, completed_datetime: datetime):

		self.__transmission_guid = transmission_guid
		self.__source_device_guid = source_device_guid
		self.__source_client_guid = source_client_guid
		self.__transmission_json_string = transmission_json_string
		self.__destination_device_guid = destination_device_guid
		self.__dequeue_client_guid = dequeue_client_guid
		self.__dequeue_token_guid = dequeue_token_guid
		self.__completed_client_guid = completed_client_guid
		self.__row_created_datetime = row_created_datetime
		self.__dequeued_datetime = dequeued_datetime
		self.__completed_datetime = completed_datetime

	def get_transmission_guid(self) -> str:
		return self.__transmission_guid

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

	def get_dequeue_token_guid(self) -> str:
		return self.__dequeue_token_guid

	def get_completed_client_guid(self) -> str:
		return self.__completed_client_guid

	def get_row_created_datetime(self) -> datetime:
		return self.__row_created_datetime

	def get_dequeued_datetime(self) -> datetime:
		return self.__dequeued_datetime

	def get_completed_datetime(self) -> datetime:
		return self.__completed_datetime

	def to_json(self) -> object:
		return {
			"transmission_guid": self.__transmission_guid,
			"source_device_guid": self.__source_device_guid,
			"source_client_guid": self.__source_client_guid,
			"transmission_json_string": self.__transmission_json_string,
			"destination_device_guid": self.__destination_device_guid,
			"dequeue_client_guid": self.__dequeue_client_guid,
			"dequeue_token_guid": self.__dequeue_token_guid,
			"completed_client_guid": self.__completed_client_guid,
			"row_created_datetime": self.__row_created_datetime.strftime("%Y-%m-%d %H:%M:%S.%f") if self.__row_created_datetime is not None else None,
			"dequeued_datetime": self.__dequeued_datetime.strftime("%Y-%m-%d %H:%M:%S.%f") if self.__dequeued_datetime is not None else None,
			"completed_datetime": self.__completed_datetime.strftime("%Y-%m-%d %H:%M:%S.%f") if self.__completed_datetime is not None else None
		}


class Database():

	def __init__(self):

		self.__connection = sqlite3.connect(":memory:")

		self.__initialize()

	def __initialize(self):

		_cursor = self.__connection.cursor()
		_cursor.execute("CREATE TABLE device (device_guid GUID PRIMARY KEY, purpose_id INTEGER, last_known_datetime TIMESTAMP, is_active INTEGER)")
		_cursor.execute("CREATE TABLE client (client_guid GUID PRIMARY KEY, ip_address TEXT, UNIQUE(ip_address))")
		_cursor.execute("CREATE TABLE transmission (transmission_guid GUID PRIMARY KEY, source_device_guid GUID, source_client_guid GUID, transmission_json_string TEXT, destination_device_guid GUID, dequeue_client_guid GUID, dequeue_token_guid GUID, completed_client_guid GUID, row_created_datetime TIMESTAMP, dequeued_datetime TIMESTAMP, completed_datetime TIMESTAMP)")

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

		_transmission_guid = str(uuid.uuid4())
		_row_created_datetime = datetime.utcnow()

		_insert_cursor = self.__connection.cursor()
		_insert_cursor.execute("INSERT INTO transmission (transmission_guid, source_device_guid, source_client_guid, transmission_json_string, destination_device_guid, dequeue_client_guid, dequeue_token_guid, completed_client_guid, row_created_datetime, dequeued_datetime, completed_datetime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (_transmission_guid, source_device_guid, client_guid, transmission_json_string, destination_device_guid, None, None, None, _row_created_datetime, None, None))

		_transmission = Transmission(
			transmission_guid=_transmission_guid,
			source_device_guid=source_device_guid,
			source_client_guid=client_guid,
			transmission_json_string=transmission_json_string,
			destination_device_guid=destination_device_guid,
			dequeue_client_guid=None,
			dequeue_token_guid=None,
			completed_client_guid=None,
			row_created_datetime=_row_created_datetime,
			dequeued_datetime=None,
			completed_datetime=None
		)
		return _transmission

	def get_next_transmission(self, *, client_guid: str) -> Transmission:

		_dequeue_token_guid = str(uuid.uuid4())
		_dequeued_datetime = datetime.utcnow()

		_update_cursor = self.__connection.cursor()
		_update_cursor.execute("UPDATE transmission SET dequeue_client_guid = ?, dequeue_token_guid = ?, dequeued_datetime = ? WHERE transmission_guid = (SELECT t_inner.transmission_guid FROM transmission AS t_inner WHERE t_inner.dequeue_token_guid IS NULL ORDER BY t_inner.row_created_datetime LIMIT 1)", (client_guid, _dequeue_token_guid, _dequeued_datetime))

		_get_cursor = self.__connection.cursor()
		_get_result = _get_cursor.execute("SELECT transmission_guid, source_device_guid, source_client_guid, transmission_json_string, destination_device_guid, row_created_datetime FROM transmission WHERE dequeue_token_guid = ?", (_dequeue_token_guid, ))

		_rows = _get_result.fetchall()
		if len(_rows) == 0:
			_transmission = None
		else:
			_row = _rows[0]

			_transmission = Transmission(
				transmission_guid=_row[0],
				source_device_guid=_row[1],
				source_client_guid=_row[2],
				transmission_json_string=_row[3],
				destination_device_guid=_row[4],
				dequeue_client_guid=client_guid,
				dequeue_token_guid=_dequeue_token_guid,
				completed_client_guid=None,
				row_created_datetime=datetime.strptime(_row[5], "%Y-%m-%d %H:%M:%S.%f"),
				dequeued_datetime=_dequeued_datetime,
				completed_datetime=None
			)
		return _transmission

	def transmission_completed(self, *, client_guid: str, transmission_guid: str):

		_completed_datetime = datetime.utcnow()

		_update_cursor = self.__connection.cursor()
		_update_cursor.execute("UPDATE transmission SET completed_client_guid = ?, completed_datetime = ? WHERE transmission_guid = ?", (client_guid, _completed_datetime, transmission_guid))

		_get_cursor = self.__connection.cursor()
		_get_result = _get_cursor.execute("SELECT transmission_guid, source_device_guid, source_client_guid, transmission_json_string, destination_device_guid, dequeue_client_guid, dequeue_token_guid, row_created_datetime, dequeued_datetime FROM transmission WHERE transmission_guid = ?", (transmission_guid,))

		_rows = _get_result.fetchall()
		if len(_rows) == 0:
			_transmission = None
		else:
			_row = _rows[0]

			_transmission = Transmission(
				transmission_guid=_row[0],
				source_device_guid=_row[1],
				source_client_guid=_row[2],
				transmission_json_string=_row[3],
				destination_device_guid=_row[4],
				dequeue_client_guid=_row[5],
				dequeue_token_guid=_row[6],
				completed_client_guid=client_guid,
				row_created_datetime=datetime.strptime(_row[7], "%Y-%m-%d %H:%M:%S.%f"),
				dequeued_datetime=datetime.strptime(_row[8], "%Y-%m-%d %H:%M:%S.%f"),
				completed_datetime=_completed_datetime
			)
		return _transmission
