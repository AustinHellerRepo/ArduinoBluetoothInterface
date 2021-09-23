from __future__ import annotations
from enum import IntEnum
import sqlite3
import uuid
from datetime import datetime
from typing import Tuple, List, Dict
import threading


class Purpose(IntEnum):

	DoorLight = 1,
	DeskController = 2


class ApiEntrypoint(IntEnum):

	TestGet = 1,
	TestPost = 2,
	TestJson = 3,
	V1ReceiveDeviceAnnouncement = 4,
	V1ReceiveDeviceTransmission = 5,
	V1ListDevices = 6,
	V1GetUuid = 7


class Client():

	def __init__(self, *, client_guid: str, ip_address: str):

		self.__client_guid = client_guid
		self.__ip_address = ip_address

	def get_client_guid(self) -> str:
		return self.__client_guid

	def get_ip_address(self) -> str:
		return self.__ip_address

	def to_json(self) -> object:
		return {
			"client_guid": self.__client_guid,
			"ip_address": self.__ip_address
		}

	@staticmethod
	def parse_row(*, row: Dict) -> Client:
		if len(row) != 2:
			raise Exception(f"Unexpected number of columns in row. Expected 2, found {len(row)}.")
		else:
			return Client(
				client_guid=row[0],
				ip_address=row[1]
			)


class ApiEntrypointLog():

	def __init__(self, *, api_entrypoint_log_id: int, api_entrypoint_id: int, request_client_guid: str, input_json_string: str, row_created_datetime: datetime):

		self.__api_entrypoint_log_id = api_entrypoint_log_id
		self.__api_entrypoint_id = api_entrypoint_id
		self.__request_client_guid = request_client_guid
		self.__input_json_string = input_json_string
		self.__row_created_datetime = row_created_datetime

	def get_api_entrypoint_log_id(self) -> int:
		return self.__api_entrypoint_log_id

	def get_api_entrypoint(self) -> ApiEntrypoint:
		return ApiEntrypoint(self.__api_entrypoint_id)

	def get_request_client_guid(self) -> str:
		return self.__request_client_guid

	def get_input_json_string(self) -> str:
		return self.__input_json_string

	def get_row_created_datetime(self) -> datetime:
		return self.__row_created_datetime

	@staticmethod
	def parse_row(*, row: Dict) -> ApiEntrypointLog:
		if len(row) != 5:
			raise Exception(f"Unexpected number of columns in row. Expected 5, found {len(row)}.")
		else:
			return ApiEntrypointLog(
				api_entrypoint_log_id=row[0],
				api_entrypoint_id=row[1],
				request_client_guid=row[2],
				input_json_string=row[3],
				row_created_datetime=datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f")
			)


class Device():

	def __init__(self, *, device_guid: str, purpose_guid: str, socket_port: int, last_known_client_guid: str, last_known_datetime: datetime):

		self.__device_guid = device_guid
		self.__purpose_guid = purpose_guid
		self.__socket_port = socket_port
		self.__last_known_client_guid = last_known_client_guid
		self.__last_known_datetime = last_known_datetime

		self.__last_known_client = None  # type: Client

	def get_device_guid(self) -> str:
		return self.__device_guid

	def get_purpose_guid(self) -> str:
		return self.__purpose_guid

	def get_socket_port(self) -> int:
		return self.__socket_port

	def get_last_known_client_guid(self) -> str:
		return self.__last_known_client_guid

	def get_last_known_datetime(self) -> datetime:
		return self.__last_known_datetime

	def set_last_known_client(self, *, last_known_client: Client):
		self.__last_known_client = last_known_client

	def get_last_known_client(self) -> Client:
		return self.__last_known_client

	def to_json(self) -> object:
		return {
			"device_guid": self.__device_guid,
			"purpose_guid": self.__purpose_guid,
			"socket_port": self.__socket_port,
			"last_known_client_guid": self.__last_known_client_guid,
			"last_known_datetime": self.__last_known_datetime.strftime("%Y-%m-%d %H:%M:%S.%f") if self.__last_known_datetime is not None else None,
			"last_known_client": None if self.__last_known_client is None else self.__last_known_client.to_json()
		}

	@staticmethod
	def parse_row(*, row: Dict) -> Device:
		if len(row) != 5:
			raise Exception(f"Unexpected number of columns in row. Expected 5, found {len(row)}.")
		else:
			return Device(
				device_guid=row[0],
				purpose_guid=row[1],
				socket_port=int(row[2]),
				last_known_client_guid=row[3],
				last_known_datetime=datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f"),
			)


class Queue():

	def __init__(self, *, queue_guid: str):

		self.__queue_guid = queue_guid

	def get_queue_guid(self) -> str:
		return self.__queue_guid

	def to_json(self) -> object:
		return {
			"queue_guid": self.__queue_guid
		}

	@staticmethod
	def parse_row(row: Dict) -> Queue:
		if len(row) != 1:
			raise Exception(f"Unexpected number of columns in row. Expected 1, found {len(row)}.")
		else:
			return Queue(
				queue_guid=row[0]
			)


class Transmission():

	def __init__(self, *,
				 transmission_guid: str,
				 queue_guid: str,
				 source_device_guid: str,
				 request_client_guid: str,
				 transmission_json_string: str,
				 destination_device_guid: str,
				 row_created_datetime: datetime,
				 is_retry_ready: bool
	):
		self.__transmission_guid = transmission_guid
		self.__queue_guid = queue_guid
		self.__source_device_guid = source_device_guid
		self.__request_client_guid = request_client_guid
		self.__transmission_json_string = transmission_json_string
		self.__destination_device_guid = destination_device_guid
		self.__row_created_datetime = row_created_datetime
		self.__is_retry_ready = is_retry_ready

		self.__source_device = None  # type: Device
		self.__destination_device = None  # type: Device

	def get_transmission_guid(self) -> str:
		return self.__transmission_guid

	def get_queue_guid(self) -> str:
		return self.__queue_guid

	def get_source_device_guid(self) -> str:
		return self.__source_device_guid

	def get_request_client_guid(self) -> str:
		return self.__request_client_guid

	def get_transmission_json_string(self) -> str:
		return self.__transmission_json_string

	def get_destination_device_guid(self) -> str:
		return self.__destination_device_guid

	def get_row_created_datetime(self) -> datetime:
		return self.__row_created_datetime

	def get_is_retry_ready(self) -> bool:
		return self.__is_retry_ready

	def set_source_device(self, *, source_device: Device):
		self.__source_device = source_device

	def get_source_device(self) -> Device:
		return self.__source_device

	def set_destination_device(self, *, destination_device: Device):
		self.__destination_device = destination_device

	def get_destination_device(self) -> Device:
		return self.__destination_device

	def to_json(self) -> object:
		return {
			"transmission_guid": self.__transmission_guid,
			"queue_guid": self.__queue_guid,
			"source_device_guid": self.__source_device_guid,
			"request_client_guid": self.__request_client_guid,
			"transmission_json_string": self.__transmission_json_string,
			"destination_device_guid": self.__destination_device_guid,
			"row_created_datetime": self.__row_created_datetime.strftime("%Y-%m-%d %H:%M:%S.%f") if self.__row_created_datetime is not None else None,
			"is_retry_ready": self.__is_retry_ready,
			"source_device": None if self.__source_device is None else self.__source_device.to_json(),
			"destination_device": None if self.__destination_device is None else self.__destination_device.to_json()
		}

	@staticmethod
	def parse_row(*, row: Dict) -> Transmission:
		if len(row) != 8:
			raise Exception(f"Unexpected number of columns in row. Expected 8, found {len(row)}.")
		else:
			return Transmission(
				transmission_guid=row[0],
				queue_guid=row[1],
				source_device_guid=row[2],
				request_client_guid=row[3],
				transmission_json_string=row[4],
				destination_device_guid=row[5],
				row_created_datetime=datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S.%f"),
				is_retry_ready=row[7]
			)


class TransmissionDequeue():

	def __init__(self, *,
				 transmission_dequeue_guid: str,
				 transmission_guid: str,
				 request_client_guid: str,
				 destination_client_guid: str,
				 row_created_datetime: datetime
	):
		self.__transmission_dequeue_guid = transmission_dequeue_guid
		self.__transmission_guid = transmission_guid
		self.__request_client_guid = request_client_guid
		self.__destination_client_guid = destination_client_guid
		self.__row_created_datetime = row_created_datetime

		self.__transmission = None  # type: Transmission

	def get_transmission_dequeue_guid(self) -> str:
		return self.__transmission_dequeue_guid

	def get_transmission_guid(self) -> str:
		return self.__transmission_guid

	def get_request_client_guid(self) -> str:
		return self.__request_client_guid

	def get_destination_client_guid(self) -> str:
		return self.__destination_client_guid

	def get_row_created_datetime(self) -> datetime:
		return self.__row_created_datetime

	def set_transmission(self, *, transmission: Transmission):
		self.__transmission = transmission

	def get_transmission(self) -> Transmission:
		return self.__transmission

	def to_json(self) -> object:
		return {
			"transmission_dequeue_guid": self.__transmission_dequeue_guid,
			"transmission_guid": self.__transmission_guid,
			"request_client_guid": self.__request_client_guid,
			"destination_client_guid": self.__destination_client_guid,
			"row_created_datetime": self.__row_created_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
			"transmission": None if self.__transmission is None else self.__transmission.to_json()
		}

	@staticmethod
	def parse_row(*, row: Dict) -> TransmissionDequeue:
		if len(row) != 5:
			raise Exception(f"Unexpected number of columns in row. Expected 5, found {len(row)}.")
		else:
			return TransmissionDequeue(
				transmission_dequeue_guid=row[0],
				transmission_guid=row[1],
				request_client_guid=row[2],
				destination_client_guid=row[3],
				row_created_datetime=datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f")
			)


class TransmissionDequeueErrorTransmission():

	def __init__(self, *,
				 transmission_dequeue_error_transmission_guid: str,
				 request_client_guid: str,
				 transmission_dequeue_guid: str,
				 error_message_json_string: str,
				 row_created_datetime: datetime,
				 is_retry_ready: bool
	):
		self.__transmission_dequeue_error_transmission_guid = transmission_dequeue_error_transmission_guid
		self.__request_client_guid = request_client_guid
		self.__transmission_dequeue_guid = transmission_dequeue_guid
		self.__error_message_json_string = error_message_json_string
		self.__row_created_datetime = row_created_datetime
		self.__is_retry_ready = is_retry_ready

		self.__transmission_dequeue = None  # type: TransmissionDequeue

	def get_transmission_dequeue_error_transmission_guid(self) -> str:
		return self.__transmission_dequeue_error_transmission_guid

	def get_request_client_guid(self) -> str:
		return self.__request_client_guid

	def get_transmission_dequeue_guid(self) -> str:
		return self.__transmission_dequeue_guid

	def get_error_message_json_string(self) -> str:
		return self.__error_message_json_string

	def get_row_created_datetime(self) -> datetime:
		return self.__row_created_datetime

	def get_is_retry_ready(self) -> bool:
		return self.__is_retry_ready

	def set_transmission_dequeue(self, *, transmission_dequeue: TransmissionDequeue):
		self.__transmission_dequeue = transmission_dequeue

	def get_transmission_dequeue(self) -> TransmissionDequeue:
		return self.__transmission_dequeue

	def to_json(self) -> object:
		return {
			"transmission_dequeue_error_transmission_guid": self.__transmission_dequeue_error_transmission_guid,
			"request_client_guid": self.__request_client_guid,
			"transmission_dequeue_guid": self.__transmission_dequeue_guid,
			"error_message_json_string": self.__error_message_json_string,
			"row_created_datetime": self.__row_created_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
			"is_retry_ready": self.__is_retry_ready,
			"transmission_dequeue": None if self.__transmission_dequeue is None else self.__transmission_dequeue.to_json()
		}

	@staticmethod
	def parse_row(*, row: Dict) -> TransmissionDequeueErrorTransmission:
		if len(row) != 6:
			raise Exception(f"Unexpected number of columns in row. Expected 6, found {len(row)}.")
		else:
			return TransmissionDequeueErrorTransmission(
				transmission_dequeue_error_transmission_guid=row[0],
				request_client_guid=row[1],
				transmission_dequeue_guid=row[2],
				error_message_json_string=row[3],
				row_created_datetime=datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f"),
				is_retry_ready=row[5]
			)


class TransmissionDequeueErrorTransmissionDequeue():

	def __init__(self, *,
				 transmission_dequeue_error_transmission_dequeue_guid: str,
				 transmission_dequeue_error_transmission_guid: str,
				 request_client_guid: str,
				 destination_client_guid: str,
				 row_created_datetime: datetime
	):
		self.__transmission_dequeue_error_transmission_dequeue_guid = transmission_dequeue_error_transmission_dequeue_guid
		self.__transmission_dequeue_error_transmission_guid = transmission_dequeue_error_transmission_guid
		self.__request_client_guid = request_client_guid
		self.__destination_client_guid = destination_client_guid
		self.__row_created_datetime = row_created_datetime

		self.__transmission_dequeue_error_transmission = None  # type: TransmissionDequeueErrorTransmission
		self.__destination_client = None  # type: Client

	def get_transmission_dequeue_error_transmission_dequeue_guid(self) -> str:
		return self.__transmission_dequeue_error_transmission_dequeue_guid

	def get_transmission_dequeue_error_transmission_guid(self) -> str:
		return self.__transmission_dequeue_error_transmission_guid

	def get_request_client_guid(self) -> str:
		return self.__request_client_guid

	def get_destination_client_guid(self) -> str:
		return self.__destination_client_guid

	def get_row_created_datetime(self) -> datetime:
		return self.__row_created_datetime

	def set_transmission_dequeue_error_transmission(self, *, transmission_dequeue_error_transmission: TransmissionDequeueErrorTransmission):
		self.__transmission_dequeue_error_transmission = transmission_dequeue_error_transmission

	def get_transmission_dequeue_error_transmission(self) -> TransmissionDequeueErrorTransmission:
		return self.__transmission_dequeue_error_transmission

	def set_destination_client(self, *, destination_client: Client):
		self.__destination_client = destination_client

	def get_destination_client(self) -> Client:
		return self.__destination_client

	def to_json(self) -> object:
		return {
			"transmission_dequeue_error_transmission_dequeue_guid": self.__transmission_dequeue_error_transmission_dequeue_guid,
			"transmission_dequeue_error_transmission_guid": self.__transmission_dequeue_error_transmission_guid,
			"request_client_guid": self.__request_client_guid,
			"destination_client_guid": self.__destination_client_guid,
			"row_created_datetime": self.__row_created_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
			"destination_client": None if self.__destination_client is None else self.__destination_client.to_json(),
			"transmission_dequeue_error_transmission": None if self.__transmission_dequeue_error_transmission is None else self.__transmission_dequeue_error_transmission.to_json()
		}

	@staticmethod
	def parse_row(*, row: Dict) -> TransmissionDequeueErrorTransmissionDequeue:
		if len(row) != 5:
			raise Exception(f"Unexpected number of columns in row. Expected 5, found {len(row)}.")
		else:
			return TransmissionDequeueErrorTransmissionDequeue(
				transmission_dequeue_error_transmission_dequeue_guid=row[0],
				transmission_dequeue_error_transmission_guid=row[1],
				request_client_guid=row[2],
				destination_client_guid=row[3],
				row_created_datetime=datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f")
			)


class Database():

	def __init__(self):

		#self.__connection = sqlite3.connect(":memory:;foreign keys=true;")
		self.__connection = sqlite3.connect(":memory:", check_same_thread=False)

		self.__connection_semaphore = threading.Semaphore()
		self.__connection.isolation_level = None
		self.__drop_tables_if_exist = False

		self.__initialize()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.dispose()

	def __initialize(self):

		_cursor = self.__connection.cursor()
		_cursor.execute('''
			PRAGMA foreign_keys = ON;
		''')

		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS client;")
		_cursor.execute('''
			CREATE TABLE client
			(
				client_guid GUID PRIMARY KEY,
				ip_address TEXT,
				UNIQUE(ip_address)
			)
		''')
		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS queue;")
		_cursor.execute('''
			CREATE TABLE queue
			(
				queue_guid GUID PRIMARY KEY,
				row_created_datetime TIMESTAMP
			)
		''')
		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS device;")
		_cursor.execute('''
			CREATE TABLE device
			(
				device_guid GUID PRIMARY KEY,
				purpose_guid GUID,
				socket_port INTEGER,
				last_known_client_guid GUID,
				last_known_datetime TIMESTAMP,
				row_created_datetime TIMESTAMP,
				FOREIGN KEY (last_known_client_guid) REFERENCES client(client_guid)
			)
		''')
		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS transmission;")
		_cursor.execute('''
			CREATE TABLE transmission
			(
				transmission_guid GUID PRIMARY KEY,
				queue_guid GUID,
				source_device_guid GUID,
				request_client_guid GUID,
				transmission_json_string TEXT,
				destination_device_guid GUID,
				row_created_datetime TIMESTAMP,
				is_retry_ready INTEGER,
				FOREIGN KEY (queue_guid) REFERENCES queue(queue_guid),
				FOREIGN KEY (source_device_guid) REFERENCES device(device_guid),
				FOREIGN KEY (request_client_guid) REFERENCES client(client_guid),
				FOREIGN KEY (destination_device_guid) REFERENCES device(device_guid)
			)
		''')
		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS transmission_dequeue;")
		_cursor.execute('''
			CREATE TABLE transmission_dequeue
			(
				transmission_dequeue_guid GUID PRIMARY KEY,
				transmission_guid GUID,
				request_client_guid GUID,
				destination_client_guid GUID,
				row_created_datetime TIMESTAMP,
				FOREIGN KEY (transmission_guid) REFERENCES transmission(transmission_guid),
				FOREIGN KEY (request_client_guid) REFERENCES client(client_guid),
				FOREIGN KEY (destination_client_guid) REFERENCES client(client_guid)
			)
		''')
		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS transmission_complete;")
		_cursor.execute('''
			CREATE TABLE transmission_complete
			(
				transmission_complete_guid GUID PRIMARY KEY,
				transmission_dequeue_guid GUID,
				request_client_guid GUID,
				row_created_datetime TIMESTAMP,
				FOREIGN KEY (transmission_dequeue_guid) REFERENCES transmission_dequeue(transmission_dequeue_guid),
				FOREIGN KEY (request_client_guid) REFERENCES client(client_guid)
			)
		''')
		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS transmission_dequeue_error_transmission;")
		_cursor.execute('''
			CREATE TABLE transmission_dequeue_error_transmission
			(
				transmission_dequeue_error_transmission_guid GUID PRIMARY KEY,
				transmission_dequeue_guid GUID,
				request_client_guid GUID,
				error_message_json_string TEXT,
				row_created_datetime TIMESTAMP,
				is_retry_ready INTEGER,
				FOREIGN KEY (request_client_guid) REFERENCES client(client_guid),
				FOREIGN KEY (transmission_dequeue_guid) REFERENCES transmission_dequeue(transmission_dequeue_guid)
			)
		''')
		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS transmission_dequeue_error_transmission_dequeue;")
		_cursor.execute('''
			CREATE TABLE transmission_dequeue_error_transmission_dequeue
			(
				transmission_dequeue_error_transmission_dequeue_guid GUID PRIMARY KEY,
				transmission_dequeue_error_transmission_guid GUID,
				request_client_guid GUID,
				destination_client_guid GUID,
				row_created_datetime TIMESTAMP,
				FOREIGN KEY (transmission_dequeue_error_transmission_guid) REFERENCES transmission_dequeue_error_transmission(transmission_dequeue_error_transmission_guid),
				FOREIGN KEY (request_client_guid) REFERENCES client(client_guid),
				FOREIGN KEY (destination_client_guid) REFERENCES client(client_guid)
			)
		''')
		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS transmission_dequeue_error_transmission_complete;")
		_cursor.execute('''
			CREATE TABLE transmission_dequeue_error_transmission_complete
			(
				transmission_dequeue_error_transmission_complete_guid GUID PRIMARY KEY,
				transmission_dequeue_error_transmission_dequeue_guid GUID,
				request_client_guid GUID,
				is_retry_requested INTEGER,
				row_created_datetime TIMESTAMP,
				FOREIGN KEY (transmission_dequeue_error_transmission_dequeue_guid) REFERENCES transmission_dequeue_error_transmission_dequeue(transmission_dequeue_error_transmission_dequeue_guid),
				FOREIGN KEY (request_client_guid) REFERENCES client(client_guid)
			)
		''')
		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS transmission_dequeue_error_transmission_error;")
		_cursor.execute('''
			CREATE TABLE transmission_dequeue_error_transmission_error
			(
				transmission_dequeue_error_transmission_error_guid GUID PRIMARY KEY,
				transmission_dequeue_error_transmission_dequeue_guid GUID,
				request_client_guid GUID,
				error_message_json_string TEXT,
				row_created_datetime TIMESTAMP,
				FOREIGN KEY (transmission_dequeue_error_transmission_dequeue_guid) REFERENCES transmission_dequeue_error_transmission_dequeue(transmission_dequeue_error_transmission_dequeue_guid),
				FOREIGN KEY (request_client_guid) REFERENCES client(client_guid)
			)
		''')
		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS api_entrypoint;")
		_cursor.execute('''
			CREATE TABLE api_entrypoint
			(
				api_entrypoint_id INTEGER PRIMARY KEY,
				name TEXT
			)
		''')
		for _api_entrypoint in list(ApiEntrypoint):
			_cursor.execute('''
				INSERT INTO api_entrypoint
				(
					api_entrypoint_id,
					name
				)
				VALUES
				(
					?,
					?
				)
		''', (int(_api_entrypoint), str(_api_entrypoint)))
		if self.__drop_tables_if_exist:
			_cursor.execute("DROP TABLE IF EXISTS api_entrypoint_log;")
		_cursor.execute('''
			CREATE TABLE api_entrypoint_log
			(
				api_entrypoint_log_id INTEGER PRIMARY KEY AUTOINCREMENT,
				api_entrypoint_id INTEGER,
				request_client_guid GUID,
				input_json_string TEXT,
				row_created_datetime TIMESTAMP,
				FOREIGN KEY (api_entrypoint_id) REFERENCES api_entrypoint(api_entrypoint_id),
				FOREIGN KEY (request_client_guid) REFERENCES client(client_guid)
			)
		''')

	def dispose(self):

		self.__connection_semaphore.acquire()

		self.__connection.close()

		self.__connection_semaphore.release()

	def insert_client(self, *, ip_address: str) -> Client:

		self.__connection_semaphore.acquire()

		try:
			_client_guid = str(uuid.uuid4()).upper()

			_insert_cursor = self.__connection.cursor()
			_insert_cursor.execute('''
				INSERT OR IGNORE INTO client
				(
					client_guid,
					ip_address
				)
				VALUES (?, ?)
			''', (_client_guid, ip_address))

			_get_guid_cursor = self.__connection.cursor()
			_get_guid_result = _get_guid_cursor.execute('''
				SELECT
					c.client_guid,
					c.ip_address
				FROM client AS c
				WHERE
					ip_address = ?
			''', (ip_address, ))

			_rows = _get_guid_result.fetchall()
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		if len(_rows) != 1:
			raise Exception(f"Unexpected number of rows. Expected 1, found {len(_rows)}.")
		else:
			_client = Client.parse_row(
				row=_rows[0]
			)

		return _client

	def insert_api_entrypoint_log(self, *, client_guid: str, api_entrypoint: ApiEntrypoint, input_json_string: str):

		self.__connection_semaphore.acquire()

		try:
			_row_created_datetime = datetime.utcnow()

			_insert_cursor = self.__connection.cursor()
			_insert_cursor.execute('''
				INSERT INTO api_entrypoint_log
				(
					api_entrypoint_log_id,
					api_entrypoint_id,
					request_client_guid,
					input_json_string,
					row_created_datetime
				)
				VALUES (?, ?, ?, ?, ?)
			''', (None, int(api_entrypoint), client_guid, input_json_string, _row_created_datetime))
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

	def insert_device(self, *, device_guid: str, client_guid: str, purpose_guid: str, socket_port: int) -> Device:

		self.__connection_semaphore.acquire()

		try:
			_insert_cursor = self.__connection.cursor()
			_insert_cursor.execute('''
				INSERT OR IGNORE INTO device
				(
					device_guid,
					purpose_guid,
					socket_port,
					last_known_client_guid,
					last_known_datetime
				)
				VALUES (?, ?, ?, ?, ?)
			''', (device_guid, purpose_guid, socket_port, client_guid, datetime.utcnow()))

			_update_known_datetime_cursor = self.__connection.cursor()
			_update_known_datetime_cursor.execute('''
				UPDATE device
				SET
					purpose_guid = ?,
					socket_port = ?,
					last_known_client_guid = ?,
					last_known_datetime = ?
				WHERE
					device_guid = ?
			''', (purpose_guid, socket_port, client_guid, datetime.utcnow(), device_guid))

			_transmission_retry_cursor = self.__connection.cursor()
			_transmission_retry_cursor.execute('''
				UPDATE transmission
				SET
					is_retry_ready = 1
				WHERE
					is_retry_ready = 0
					AND destination_device_guid = ?
			''', (device_guid,))

			_error_retry_cursor = self.__connection.cursor()
			_error_retry_cursor.execute('''
				UPDATE transmission_dequeue_error_transmission
				SET
					is_retry_ready = 1
				WHERE EXISTS (
					SELECT 1
					FROM transmission_dequeue AS td
					INNER JOIN transmission AS t
					ON
						t.transmission_guid = td.transmission_guid
					WHERE
						td.transmission_dequeue_guid = transmission_dequeue_error_transmission.transmission_dequeue_guid
						AND t.source_device_guid = ?
				)
				AND is_retry_ready = 0
			''', (device_guid,))
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		_is_successful, _device = self.try_get_device(
			device_guid=device_guid
		)

		if not _is_successful:
			raise Exception(f"Failed to insert device with guid: \"{device_guid}\".")

		return _device

	def insert_queue(self, *, queue_guid: str) -> Queue:

		self.__connection_semaphore.acquire()

		try:
			_row_created_datetime = datetime.utcnow()

			_insert_cursor = self.__connection.cursor()
			_insert_cursor.execute('''
				INSERT OR IGNORE INTO queue
				(
					queue_guid,
					row_created_datetime
				)
				VALUES (?, ?)
			''', (queue_guid, _row_created_datetime))
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		_queue = self.get_queue(
			queue_guid=queue_guid
		)

		return _queue

	def get_queue(self, *, queue_guid: str) -> Queue:

		self.__connection_semaphore.acquire()

		try:
			_select_cursor = self.__connection.cursor()
			_select_result = _select_cursor.execute('''
				SELECT
					q.queue_guid
				FROM queue AS q
				WHERE
					q.queue_guid = ?
			''', (queue_guid,))

			_rows = _select_result.fetchall()
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		if len(_rows) != 1:
			raise Exception(f"Unexpected number of rows. Expected 1, found {len(_rows)}.")
		else:

			_row = _rows[0]

			_queue = Queue.parse_row(
				row=_row
			)

		return _queue

	def get_all_devices(self) -> List[Device]:

		self.__connection_semaphore.acquire()

		try:
			_get_cursor = self.__connection.cursor()
			_get_result = _get_cursor.execute('''
				SELECT
					d.device_guid,
					d.purpose_guid,
					d.socket_port,
					d.last_known_client_guid,
					d.last_known_datetime
				FROM device AS d
			''')

			_rows = _get_result.fetchall()
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		_devices = []  # type: List[Device]

		for _row in _rows:

			_device = Device.parse_row(
				row=_row
			)

			_is_successful, _last_known_client = self.try_get_client(
				client_guid=_device.get_last_known_client_guid()
			)

			if not _is_successful:
				raise Exception(f"Failed to find client guid \"{_device.get_last_known_client_guid()}\" for device guid \"{_device.get_device_guid()}\".")
			else:
				_device.set_last_known_client(
					last_known_client=_last_known_client
				)

			_devices.append(_device)

		return _devices

	def insert_transmission(self, *, queue_guid: str, source_device_guid: str, client_guid: str, transmission_json_string: str, destination_device_guid: str) -> Transmission:

		self.__connection_semaphore.acquire()

		try:
			_transmission_guid = str(uuid.uuid4()).upper()
			_row_created_datetime = datetime.utcnow()

			_insert_cursor = self.__connection.cursor()
			_insert_cursor.execute('''
				INSERT INTO transmission
				(
					transmission_guid,
					queue_guid,
					source_device_guid,
					request_client_guid,
					transmission_json_string,
					destination_device_guid,
					row_created_datetime,
					is_retry_ready
				) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
			''', (_transmission_guid, queue_guid, source_device_guid, client_guid, transmission_json_string, destination_device_guid, _row_created_datetime, None))
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		_is_successful, _transmission = self.try_get_transmission(
			transmission_guid=_transmission_guid
		)

		if not _is_successful:
			raise Exception(f"Failed to insert transmission with guid: \"{_transmission_guid}\".")

		return _transmission

	def try_get_transmission(self, *, transmission_guid: str) -> Tuple[bool, Transmission]:

		self.__connection_semaphore.acquire()

		try:
			_get_cursor = self.__connection.cursor()
			_get_result = _get_cursor.execute('''
				SELECT
					transmission_guid,
					queue_guid,
					source_device_guid,
					request_client_guid,
					transmission_json_string,
					destination_device_guid,
					row_created_datetime,
					is_retry_ready
				FROM transmission
				WHERE
					transmission_guid = ?
			''', (transmission_guid,))

			_rows = _get_result.fetchall()
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		if len(_rows) == 0:
			_transmission = None
		elif len(_rows) > 1:
			raise Exception(f"Unexpected number of rows. Expected 0 or 1, found {len(_rows)}.")
		else:
			_row = _rows[0]

			_transmission = Transmission.parse_row(
				row=_row
			)

			_is_successful, _destination_device = self.try_get_device(
				device_guid=_transmission.get_destination_device_guid()
			)

			if not _is_successful:
				raise Exception(f"Failed to find device with guid: {_transmission.get_destination_device_guid()}")
			else:

				_transmission.set_destination_device(
					destination_device=_destination_device
				)

		return _transmission is not None, _transmission

	def try_get_device(self, *, device_guid: str) -> Tuple[bool, Device]:

		self.__connection_semaphore.acquire()

		try:
			_get_cursor = self.__connection.cursor()
			_get_result = _get_cursor.execute('''
				SELECT
					d.device_guid,
					d.purpose_guid,
					d.socket_port,
					d.last_known_client_guid,
					d.last_known_datetime
				FROM device AS d
				WHERE
					d.device_guid = ?
			''', (device_guid,))

			_rows = _get_result.fetchall()
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		if len(_rows) == 0:
			_device = None
		elif len(_rows) > 1:
			raise Exception(f"Unexpected number of rows. Expected 0 or 1, found {len(_rows)}.")
		else:
			_row = _rows[0]
			_device = Device.parse_row(
				row=_row
			)

			_is_successful, _last_known_client = self.try_get_client(
				client_guid=_device.get_last_known_client_guid()
			)
			if not _is_successful:
				raise Exception(f"Failed to find client guid \"{_device.get_last_known_client_guid()}\" for device guid \"{_device.get_device_guid()}\".")
			else:
				_device.set_last_known_client(
					last_known_client=_last_known_client
				)

		return _device is not None, _device

	def try_get_transmission_dequeue(self, *, transmission_dequeue_guid: str) -> Tuple[bool, TransmissionDequeue]:

		self.__connection_semaphore.acquire()

		try:
			_get_cursor = self.__connection.cursor()
			_get_result = _get_cursor.execute('''
				SELECT
					transmission_dequeue_guid,
					transmission_guid,
					request_client_guid,
					destination_client_guid,
					row_created_datetime
				FROM transmission_dequeue
				WHERE
					transmission_dequeue_guid = ?
			''', (transmission_dequeue_guid,))

			_rows = _get_result.fetchall()
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		if len(_rows) == 0:
			_transmission_dequeue = None
		elif len(_rows) > 1:
			raise Exception(f"Unexpected number of rows. Expected 0 or 1, found {len(_rows)}.")
		else:
			_row = _rows[0]

			_transmission_dequeue = TransmissionDequeue.parse_row(
				row=_row
			)

			_is_successful, _transmission = self.try_get_transmission(
				transmission_guid=_transmission_dequeue.get_transmission_guid()
			)

			if not _is_successful:
				raise Exception(f"Failed to find transmission with guid: \"{_transmission_dequeue.get_transmission_guid()}\".")
			else:

				_transmission_dequeue.set_transmission(
					transmission=_transmission
				)

		return _transmission_dequeue is not None, _transmission_dequeue

	def get_next_transmission_dequeue(self, *, client_guid: str) -> TransmissionDequeue:

		self.__connection_semaphore.acquire()

		try:
			_transmission_dequeue_guid = str(uuid.uuid4()).upper()
			_row_created_datetime = datetime.utcnow()

			_insert_cursor = self.__connection.cursor()
			_insert_cursor.execute('''
				BEGIN
			''')
			_insert_cursor.execute('''
				INSERT INTO transmission_dequeue
				(
					transmission_dequeue_guid,
					transmission_guid,
					request_client_guid,
					destination_client_guid,
					row_created_datetime
				)
				SELECT
					?,
					t.transmission_guid,
					?,
					d.last_known_client_guid,
					?
				FROM transmission AS t
				INNER JOIN device AS d 
				ON 
					d.device_guid = t.destination_device_guid
				WHERE
					(
						NOT EXISTS ( -- there does not exist an active transmission
							SELECT 1
							FROM transmission_dequeue AS td_inner
							WHERE
								td_inner.transmission_guid = t.transmission_guid
						)
						OR
						( -- or this specific transmission needs to be retransmitted
							t.is_retry_ready = 1
						)
					)
					AND
					( -- there does not exist an earlier transmission that is not yet in a terminal state
						NOT EXISTS (
							SELECT 1
							FROM transmission AS t_earlier
							WHERE
								t_earlier.row_created_datetime < t.row_created_datetime
								AND
								( -- an earlier destination device or queued transmission
									t_earlier.destination_device_guid = t.destination_device_guid
									OR
									t_earlier.queue_guid = t.queue_guid
								)
								AND
								( -- the transmission is not in a terminal state
									NOT EXISTS ( -- not in a normal complete state
										SELECT 1
										FROM transmission_dequeue AS td_earlier
										INNER JOIN transmission_complete AS tc_earlier
										ON
											tc_earlier.transmission_dequeue_guid = td_earlier.transmission_dequeue_guid
										WHERE
											td_earlier.transmission_guid = t_earlier.transmission_guid
									)
									AND NOT EXISTS ( -- not in an failed transmission completed where a retry was not requested (basically cancelling the transmission after it failed to be sent to the destination)
										SELECT 1
										FROM transmission_dequeue AS td_earlier
										INNER JOIN transmission_dequeue_error_transmission AS tdet_earlier
										ON
											tdet_earlier.transmission_dequeue_guid = td_earlier.transmission_dequeue_guid
										INNER JOIN transmission_dequeue_error_transmission_dequeue AS tdetd_earlier
										ON
											tdetd_earlier.transmission_dequeue_error_transmission_guid = tdet_earlier.transmission_dequeue_error_transmission_guid
										INNER JOIN transmission_dequeue_error_transmission_complete AS tdetc_earlier
										ON
											tdetc_earlier.transmission_dequeue_error_transmission_dequeue_guid = tdetd_earlier.transmission_dequeue_error_transmission_dequeue_guid
										WHERE
											td_earlier.transmission_guid = t_earlier.transmission_guid
											AND tdetc_earlier.is_retry_requested = 0
									)
								)
								-- entries in the transmission_dequeue_error_transmission_error table are not valid terminal conditions because the transmissions may need to be received sequentially via a retry
						)
					)
				ORDER BY
					t.row_created_datetime
				LIMIT 1
			''', (_transmission_dequeue_guid, client_guid, _row_created_datetime))
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		_is_successful, _transmission_dequeue = self.try_get_transmission_dequeue(
			transmission_dequeue_guid=_transmission_dequeue_guid
		)

		self.__connection_semaphore.acquire()

		try:
			if _is_successful:

				if _transmission_dequeue.get_transmission().get_is_retry_ready():
					_insert_cursor.execute('''
						UPDATE transmission
						SET
							is_retry_ready = NULL
						WHERE
							transmission_guid = ?
					''', (_transmission_dequeue.get_transmission_guid(),))

			_insert_cursor.execute('''
				COMMIT
			''')
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		return _transmission_dequeue

	def transmission_completed(self, *, client_guid: str, transmission_dequeue_guid: str):

		self.__connection_semaphore.acquire()

		try:
			_transmission_complete_guid = str(uuid.uuid4()).upper()
			_row_created_datetime = datetime.utcnow()

			_insert_cursor = self.__connection.cursor()
			_insert_cursor.execute('''
				INSERT INTO transmission_complete
				(
					transmission_complete_guid,
					transmission_dequeue_guid,
					request_client_guid,
					row_created_datetime
				)
				VALUES (?, ?, ?, ?)
			''', (_transmission_complete_guid, transmission_dequeue_guid, client_guid, _row_created_datetime))
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

	def transmission_failed(self, *, client_guid: str, transmission_dequeue_guid: str, error_message_json_string: str) -> TransmissionDequeueErrorTransmission:

		self.__connection_semaphore.acquire()

		try:
			_transmission_dequeue_error_transmission_guid = str(uuid.uuid4()).upper()
			_row_created_datetime = datetime.utcnow()

			_insert_cursor = self.__connection.cursor()
			_insert_cursor.execute('''
				INSERT INTO transmission_dequeue_error_transmission
				(
					transmission_dequeue_error_transmission_guid,
					request_client_guid,
					transmission_dequeue_guid,
					error_message_json_string,
					row_created_datetime,
					is_retry_ready
				)
				VALUES (?, ?, ?, ?, ?, ?)
			''', (_transmission_dequeue_error_transmission_guid, client_guid, transmission_dequeue_guid, error_message_json_string, _row_created_datetime, None))
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		_is_successful, _transmission_dequeue_error_transmission = self.try_get_transmission_dequeue_error_transmission(
			transmission_dequeue_error_transmission_guid=_transmission_dequeue_error_transmission_guid
		)

		if not _is_successful:
			raise Exception(f"Failed to insert transmission_dequeue_error_transmission for transmission_dequeue_guid \"{transmission_dequeue_guid}\".")

		return _transmission_dequeue_error_transmission

	def try_get_transmission_dequeue_error_transmission_dequeue(self, *, transmission_dequeue_error_transmission_dequeue_guid: str) -> Tuple[bool, TransmissionDequeueErrorTransmissionDequeue]:

		self.__connection_semaphore.acquire()

		try:
			_get_cursor = self.__connection.cursor()
			_get_result = _get_cursor.execute('''
				SELECT
					transmission_dequeue_error_transmission_dequeue_guid,
					transmission_dequeue_error_transmission_guid,
					request_client_guid,
					destination_client_guid,
					row_created_datetime
				FROM transmission_dequeue_error_transmission_dequeue
				WHERE
					transmission_dequeue_error_transmission_dequeue_guid = ?
			''', (transmission_dequeue_error_transmission_dequeue_guid,))

			_rows = _get_result.fetchall()
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		if len(_rows) == 0:
			_transmission_dequeue_error_transmission_dequeue = None
		elif len(_rows) > 1:
			raise Exception(f"Unexpected number of rows. Expected 0 or 1, found {len(_rows)}.")
		else:
			_row = _rows[0]

			_transmission_dequeue_error_transmission_dequeue = TransmissionDequeueErrorTransmissionDequeue.parse_row(
				row=_row
			)

			_is_successful, _destination_client = self.try_get_client(
				client_guid=_transmission_dequeue_error_transmission_dequeue.get_destination_client_guid()
			)

			if not _is_successful:
				raise Exception(f"Failed to find destination client with guid: \"{_transmission_dequeue_error_transmission_dequeue.get_destination_client_guid()}\".")
			else:

				_transmission_dequeue_error_transmission_dequeue.set_destination_client(
					destination_client=_destination_client
				)

				_is_successful, _transmission_dequeue_error_transmission = self.try_get_transmission_dequeue_error_transmission(
					transmission_dequeue_error_transmission_guid=_transmission_dequeue_error_transmission_dequeue.get_transmission_dequeue_error_transmission_guid()
				)

				if not _is_successful:
					raise Exception(f"Failed to find transmission dequeue error transmission with guid: \"{_transmission_dequeue_error_transmission_dequeue.get_transmission_dequeue_error_transmission_guid()}\".")
				else:

					_transmission_dequeue_error_transmission_dequeue.set_transmission_dequeue_error_transmission(
						transmission_dequeue_error_transmission=_transmission_dequeue_error_transmission
					)

		return _transmission_dequeue_error_transmission_dequeue is not None, _transmission_dequeue_error_transmission_dequeue

	def try_get_transmission_dequeue_error_transmission(self, *, transmission_dequeue_error_transmission_guid: str) -> Tuple[bool, TransmissionDequeueErrorTransmission]:

		self.__connection_semaphore.acquire()

		try:
			_get_cursor = self.__connection.cursor()
			_get_result = _get_cursor.execute('''
				SELECT
					transmission_dequeue_error_transmission_guid,
					request_client_guid,
					transmission_dequeue_guid,
					error_message_json_string,
					row_created_datetime,
					is_retry_ready
				FROM transmission_dequeue_error_transmission
				WHERE
					transmission_dequeue_error_transmission_guid = ?
			''', (transmission_dequeue_error_transmission_guid,))

			_rows = _get_result.fetchall()
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		if len(_rows) == 0:
			_transmission_dequeue_error_transmission = None
		elif len(_rows) > 1:
			raise Exception(f"Unexpected number of rows. Expected 0 or 1, found {len(_rows)}.")
		else:
			_row = _rows[0]

			_transmission_dequeue_error_transmission = TransmissionDequeueErrorTransmission.parse_row(
				row=_row
			)

			_is_successful, _transmission_dequeue = self.try_get_transmission_dequeue(
				transmission_dequeue_guid=_transmission_dequeue_error_transmission.get_transmission_dequeue_guid()
			)

			if not _is_successful:
				raise Exception(f"Failed to find transmission dequeue with guid: \"{_transmission_dequeue_error_transmission.get_transmission_dequeue_guid()}\".")
			else:

				_transmission_dequeue_error_transmission.set_transmission_dequeue(
					transmission_dequeue=_transmission_dequeue
				)

		return _transmission_dequeue_error_transmission is not None, _transmission_dequeue_error_transmission

	def get_next_failed_transmission_dequeue(self, *, client_guid: str) -> TransmissionDequeueErrorTransmissionDequeue:

		self.__connection_semaphore.acquire()

		try:
			_transmission_dequeue_error_transmission_dequeue_guid = str(uuid.uuid4()).upper()
			_row_created_datetime = datetime.utcnow()

			_insert_cursor = self.__connection.cursor()

			_insert_cursor.execute('''
				BEGIN
			''')

			_insert_cursor.execute('''
				INSERT INTO transmission_dequeue_error_transmission_dequeue
				(
					transmission_dequeue_error_transmission_dequeue_guid,
					transmission_dequeue_error_transmission_guid,
					request_client_guid,
					destination_client_guid,
					row_created_datetime
				)
				SELECT
					?,
					tdet.transmission_dequeue_error_transmission_guid,
					?,
					d.last_known_client_guid,
					?
				FROM transmission_dequeue_error_transmission AS tdet
				INNER JOIN transmission_dequeue AS td
				ON
					td.transmission_dequeue_guid = tdet.transmission_dequeue_guid
				INNER JOIN transmission AS t
				ON
					t.transmission_guid = td.transmission_guid
				INNER JOIN device AS d 
				ON 
					d.device_guid = t.source_device_guid
				WHERE
					(
						NOT EXISTS ( -- there does not exist an active transmission
							SELECT 1
							FROM transmission_dequeue_error_transmission_dequeue AS tdetd_inner
							WHERE
								tdetd_inner.transmission_dequeue_error_transmission_guid = tdet.transmission_dequeue_error_transmission_guid
						)
						OR
						(
							tdet.is_retry_ready = 1
						)
					)
					AND
					(  -- there does not exist an earlier failed transmission not yet in a terminal state
						NOT EXISTS (
							SELECT 1
							FROM transmission_dequeue_error_transmission AS tdet_earlier
							INNER JOIN transmission_dequeue AS td_earlier
							ON
								td_earlier.transmission_dequeue_guid = tdet_earlier.transmission_dequeue_guid
							INNER JOIN transmission AS t_earlier
							ON
								t_earlier.transmission_guid = td_earlier.transmission_guid
							WHERE
								t_earlier.source_device_guid = t.source_device_guid
								AND tdet_earlier.row_created_datetime < tdet.row_created_datetime
								AND
								( -- the failed transmission is not in a terminal state
									NOT EXISTS ( -- not in a failed transaction complete state
										SELECT 1
										FROM transmission_dequeue_error_transmission_dequeue AS tdetd_earlier
										INNER JOIN transmission_dequeue_error_transmission_complete AS tdetc_earlier
										ON
											tdetc_earlier.transmission_dequeue_error_transmission_dequeue_guid = tdetd_earlier.transmission_dequeue_error_transmission_dequeue_guid
										WHERE
											tdetd_earlier.transmission_dequeue_error_transmission_guid = tdet_earlier.transmission_dequeue_error_transmission_guid
									)
									-- an entry in transmission_dequeue_error_transmission_error can occur multiple times and will not stop retrying until it succeeds
									--AND NOT EXISTS ( -- not in a failed transaction that failed state
									--	SELECT 1
									--	FROM transmission_dequeue_error_transmission_dequeue AS tdetd_earlier
									--	INNER JOIN transmission_dequeue_error_transmission_error AS tdete_earlier
									--	ON
									--		tdete_earlier.transmission_dequeue_error_transmission_dequeue_guid = tdetd_earlier.transmission_dequeue_error_transmission_dequeue_guid
									--	WHERE
									--		tdetd_earlier.transmission_dequeue_error_transmission_guid = tdet_earlier.transmission_dequeue_error_transmission_guid
									--)
								)
						)
					)
				ORDER BY
					t.row_created_datetime
				LIMIT 1
			''', (_transmission_dequeue_error_transmission_dequeue_guid, client_guid, _row_created_datetime))
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		_is_successful, _transmission_dequeue_error_transmission_dequeue = self.try_get_transmission_dequeue_error_transmission_dequeue(
			transmission_dequeue_error_transmission_dequeue_guid=_transmission_dequeue_error_transmission_dequeue_guid
		)

		self.__connection_semaphore.acquire()

		try:
			if _is_successful:

				if _transmission_dequeue_error_transmission_dequeue.get_transmission_dequeue_error_transmission().get_is_retry_ready():

					_insert_cursor.execute('''
						UPDATE transmission_dequeue_error_transmission
						SET
							is_retry_ready = NULL
						WHERE
							transmission_dequeue_error_transmission_guid = ?
					''', (_transmission_dequeue_error_transmission_dequeue.get_transmission_dequeue_error_transmission_guid(),))

			_insert_cursor.execute('''
				COMMIT
			''')
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		return _transmission_dequeue_error_transmission_dequeue

	def failed_transmission_completed(self, *, client_guid: str, transmission_dequeue_error_transmission_dequeue_guid: str, is_retry_requested: bool):

		self.__connection_semaphore.acquire()

		try:
			_transmission_dequeue_error_transmission_complete_guid = str(uuid.uuid4()).upper()
			_row_created_datetime = datetime.utcnow()

			_insert_cursor = self.__connection.cursor()
			_insert_cursor.execute('''
				BEGIN
			''')
			_insert_cursor.execute('''
				INSERT INTO transmission_dequeue_error_transmission_complete
				(
					transmission_dequeue_error_transmission_complete_guid,
					transmission_dequeue_error_transmission_dequeue_guid,
					request_client_guid,
					is_retry_requested,
					row_created_datetime
				)
				VALUES (?, ?, ?, ?, ?)
			''', (_transmission_dequeue_error_transmission_complete_guid, transmission_dequeue_error_transmission_dequeue_guid, client_guid, is_retry_requested, _row_created_datetime))
			_insert_cursor.execute('''
				UPDATE transmission
				SET
					is_retry_ready = 0
				WHERE
					? = 1
					AND EXISTS (
						SELECT 1
						FROM transmission_dequeue AS td
						INNER JOIN transmission_dequeue_error_transmission AS tdet
						ON
							tdet.transmission_dequeue_guid = td.transmission_dequeue_guid
						INNER JOIN transmission_dequeue_error_transmission_dequeue tdetd
						ON
							tdetd.transmission_dequeue_error_transmission_guid = tdet.transmission_dequeue_error_transmission_guid
						WHERE
							td.transmission_guid = transmission.transmission_guid
							AND tdetd.transmission_dequeue_error_transmission_dequeue_guid = ?
					)
			''', (is_retry_requested, transmission_dequeue_error_transmission_dequeue_guid))
			_insert_cursor.execute('''
				COMMIT
			''')
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

	def failed_transmission_failed(self, *, client_guid: str, transmission_dequeue_error_transmission_dequeue_guid: str, error_message_json_string: str):

		self.__connection_semaphore.acquire()

		try:
			_transmission_dequeue_error_transmission_error_guid = str(uuid.uuid4()).upper()
			_row_created_datetime = datetime.utcnow()

			_insert_cursor = self.__connection.cursor()
			_insert_cursor.execute('''
				BEGIN
			''')
			_insert_cursor.execute('''
				INSERT INTO transmission_dequeue_error_transmission_error
				(
					transmission_dequeue_error_transmission_error_guid,
					transmission_dequeue_error_transmission_dequeue_guid,
					request_client_guid,
					error_message_json_string,
					row_created_datetime
				)
				VALUES (?, ?, ?, ?, ?);
			''', (_transmission_dequeue_error_transmission_error_guid, transmission_dequeue_error_transmission_dequeue_guid, client_guid, error_message_json_string, _row_created_datetime))
			_insert_cursor.execute('''
				UPDATE transmission_dequeue_error_transmission
				SET 
					is_retry_ready = 0
				WHERE
					EXISTS (
						SELECT 1
						FROM transmission_dequeue_error_transmission_dequeue tdetd
						WHERE
							tdetd.transmission_dequeue_error_transmission_guid = transmission_dequeue_error_transmission.transmission_dequeue_error_transmission_guid
							AND tdetd.transmission_dequeue_error_transmission_dequeue_guid = ?
					)
			''', (transmission_dequeue_error_transmission_dequeue_guid,))
			_insert_cursor.execute('''
				COMMIT
			''')
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

	def get_devices_by_purpose(self, *, purpose_guid: str) -> List[Device]:

		self.__connection_semaphore.acquire()

		try:
			_get_cursor = self.__connection.cursor()
			_get_result = _get_cursor.execute('''
				SELECT
					d.device_guid,
					d.purpose_guid,
					d.socket_port,
					d.last_known_client_guid,
					d.last_known_datetime
				FROM device AS d
				WHERE
					d.purpose_guid = ?
			''', (purpose_guid,))

			_rows = _get_result.fetchall()
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		_devices = []  # type: List[Device]
		for _row in _rows:
			_device = Device.parse_row(
				row=_row
			)
			_is_successful, _last_known_client = self.try_get_client(
				client_guid=_device.get_last_known_client_guid()
			)
			if not _is_successful:
				raise Exception(f"Failed to find client guid \"{_device.get_last_known_client_guid()}\" for device guid \"{_device.get_device_guid()}\".")
			else:
				_device.set_last_known_client(
					last_known_client=_last_known_client
				)
			_devices.append(_device)
		return _devices

	def get_api_entrypoint_logs(self, *, inclusive_start_row_created_datetime: datetime, exclusive_end_row_created_datetime: datetime) -> List[ApiEntrypointLog]:

		self.__connection_semaphore.acquire()

		try:
			_select_cursor = self.__connection.cursor()
			_select_result = _select_cursor.execute('''
				SELECT
					ael.api_entrypoint_log_id,
					ael.api_entrypoint_id,
					ael.request_client_guid,
					ael.input_json_string,
					ael.row_created_datetime
				FROM api_entrypoint_log AS ael
				WHERE
					ael.row_created_datetime >= ?
					AND ael.row_created_datetime < ?
			''', (inclusive_start_row_created_datetime, exclusive_end_row_created_datetime))

			_rows = _select_result.fetchall()
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		_api_entrypoint_logs = []  # type: List[ApiEntrypointLog]
		for _row in _rows:
			_api_entrypoint_log = ApiEntrypointLog.parse_row(
				row=_row
			)
			_api_entrypoint_logs.append(_api_entrypoint_log)
		return _api_entrypoint_logs

	def try_get_client(self, *, client_guid: str) -> Tuple[bool, Client]:

		self.__connection_semaphore.acquire()

		try:
			_get_cursor = self.__connection.cursor()
			_get_result = _get_cursor.execute('''
				SELECT
					client_guid,
					ip_address
				FROM client
				WHERE
					client_guid = ?
			''', (client_guid,))

			_rows = _get_result.fetchall()
		except Exception as ex:
			self.__connection_semaphore.release()
			raise ex

		self.__connection_semaphore.release()

		if len(_rows) == 0:
			_client = None
		elif len(_rows) > 1:
			raise Exception(f"Unexpected number of rows. Expected 0 or 1, found {len(_rows)}.")
		else:
			_row = _rows[0]

			_client = Client.parse_row(
				row=_row
			)

		return _client is not None, _client


class DatabaseFactory():

	def __init__(self):
		self.__database = None

	def get_database(self):
		if self.__database is None:
			self.__database = Database()
		return self.__database
