from __future__ import annotations
from enum import IntEnum
import sqlite3
import uuid
from datetime import datetime
from typing import Tuple, List, Dict


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

	def __init__(self, *, device_guid: str, purpose_guid: str):

		self.__device_guid = device_guid
		self.__purpose_guid = purpose_guid

	def get_device_guid(self) -> str:
		return self.__device_guid

	def get_purpose_guid(self) -> str:
		return self.__purpose_guid

	def to_json(self) -> object:
		return {
			"device_guid": self.__device_guid,
			"purpose_guid": self.__purpose_guid
		}


class Transmission():

	def __init__(self, *,
				 transmission_guid: str,
				 source_device_guid: str,
				 request_client_guid: str,
				 transmission_json_string: str,
				 destination_device_guid: str,
				 row_created_datetime: datetime,
				 is_retry_ready: bool
	):
		self.__transmission_guid = transmission_guid
		self.__source_device_guid = source_device_guid
		self.__request_client_guid = request_client_guid
		self.__transmission_json_string = transmission_json_string
		self.__destination_device_guid = destination_device_guid
		self.__row_created_datetime = row_created_datetime
		self.__is_retry_ready = is_retry_ready

	def get_transmission_guid(self) -> str:
		return self.__transmission_guid

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

	def to_json(self) -> object:
		return {
			"transmission_guid": self.__transmission_guid,
			"source_device_guid": self.__source_device_guid,
			"request_client_guid": self.__request_client_guid,
			"transmission_json_string": self.__transmission_json_string,
			"destination_device_guid": self.__destination_device_guid,
			"row_created_datetime": self.__row_created_datetime.strftime("%Y-%m-%d %H:%M:%S.%f") if self.__row_created_datetime is not None else None,
			"is_retry_ready": self.__is_retry_ready
		}


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

		self.__transmission_dequeue = None

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

		self.__transmission_dequeue_error_transmission = None

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


class Database():

	def __init__(self):

		#self.__connection = sqlite3.connect(":memory:;foreign keys=true;")
		self.__connection = sqlite3.connect(":memory:")

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
			_cursor.execute("DROP TABLE IF EXISTS device;")
		_cursor.execute('''
			CREATE TABLE device
			(
				device_guid GUID PRIMARY KEY,
				purpose_guid GUID,
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
				source_device_guid GUID,
				request_client_guid GUID,
				transmission_json_string TEXT,
				destination_device_guid GUID,
				row_created_datetime TIMESTAMP,
				is_retry_ready INTEGER,
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
				request_client_guid GUID,
				transmission_dequeue_guid GUID,
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
				row_created_datetime TIMESTAMP,
				FOREIGN KEY (transmission_dequeue_error_transmission_dequeue_guid) REFERENCES transmission_dequeue_error_transmission_dequeue(transmission_dequeue_error_transmission_dequeue_guid),
				FOREIGN KEY (request_client_guid) REFERENCES client(client_guid)
			)
		''')

	def dispose(self):
		self.__connection.close()

	def insert_client(self, *, ip_address: str) -> Client:

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
				client_guid
			FROM client
			WHERE
				ip_address = ?
		''', (ip_address, ))

		_saved_guid = _get_guid_result.fetchall()[0][0]

		_client = Client(
			client_guid=_saved_guid,
			ip_address=ip_address
		)
		return _client

	def insert_device(self, *, device_guid: str, client_guid: str, purpose_guid: str) -> Device:

		_insert_cursor = self.__connection.cursor()
		_insert_cursor.execute('''
			INSERT OR IGNORE INTO device
			(
				device_guid,
				purpose_guid,
				last_known_client_guid,
				last_known_datetime
			)
			VALUES (?, ?, ?, ?)
		''', (device_guid, purpose_guid, client_guid, datetime.utcnow()))

		_update_known_datetime_cursor = self.__connection.cursor()
		_update_known_datetime_cursor.execute('''
			UPDATE device
			SET
				purpose_guid = ?,
				last_known_client_guid = ?,
				last_known_datetime = ?
			WHERE
				device_guid = ?
		''', (purpose_guid, client_guid, datetime.utcnow(), device_guid))

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

		_device = Device(
			device_guid=device_guid,
			purpose_guid=purpose_guid
		)
		return _device

	def get_all_devices(self) -> List[Device]:
		_get_cursor = self.__connection.cursor()
		_get_result = _get_cursor.execute('''
			SELECT
				d.device_guid,
				d.purpose_guid
			FROM device AS d
		''')
		_devices = []  # type: List[Device]
		_rows = _get_result.fetchall()
		for _row in _rows:
			_device = Device(
				device_guid=_row[0],
				purpose_guid=_row[1]
			)
			_devices.append(_device)
		return _devices

	def get_device(self, *, device_guid: str) -> Device:
		_get_cursor = self.__connection.cursor()
		_get_result = _get_cursor.execute('''
			SELECT
				d.device_guid,
				d.purpose_guid
			FROM device AS d
			WHERE
				d.device_guid = ?
		''', (device_guid,))
		_rows = _get_result.fetchall()
		if len(_rows) != 1:
			raise Exception(f"Unexpected number of devices with guid: {len(_rows)} for guid \"{device_guid}\".")
		_row = _rows[0]
		_device = Device(
			device_guid=_row[0],
			purpose_guid=_row[1]
		)
		return _device

	def insert_transmission(self, *, source_device_guid: str, client_guid: str, transmission_json_string: str, destination_device_guid: str) -> Transmission:

		_transmission_guid = str(uuid.uuid4()).upper()
		_row_created_datetime = datetime.utcnow()

		_insert_cursor = self.__connection.cursor()
		_insert_cursor.execute('''
			INSERT INTO transmission
			(
				transmission_guid,
				source_device_guid,
				request_client_guid,
				transmission_json_string,
				destination_device_guid,
				row_created_datetime,
				is_retry_ready
			) VALUES (?, ?, ?, ?, ?, ?, ?)
		''', (_transmission_guid, source_device_guid, client_guid, transmission_json_string, destination_device_guid, _row_created_datetime, None))

		_is_successful, _transmission = self.try_get_transmission(
			transmission_guid=_transmission_guid
		)

		if not _is_successful:
			raise Exception(f"Failed to insert transmission with guid: \"{_transmission_guid}\".")

		return _transmission

	def try_get_transmission(self, *, transmission_guid: str) -> Tuple[bool, Transmission]:

		_get_cursor = self.__connection.cursor()
		_get_result = _get_cursor.execute('''
			SELECT
				transmission_guid,
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
		if len(_rows) == 0:
			_transmission = None
		else:
			_row = _rows[0]

			_transmission = Transmission(
				transmission_guid=_row[0],
				source_device_guid=_row[1],
				request_client_guid=_row[2],
				transmission_json_string=_row[3],
				destination_device_guid=_row[4],
				row_created_datetime=datetime.strptime(_row[5], "%Y-%m-%d %H:%M:%S.%f"),
				is_retry_ready=_row[6]
			)

		return _transmission is not None, _transmission

	def try_get_transmission_dequeue(self, *, transmission_dequeue_guid: str) -> Tuple[bool, TransmissionDequeue]:

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
		if len(_rows) == 0:
			_transmission_dequeue = None
		else:
			_row = _rows[0]

			_transmission_dequeue = TransmissionDequeue(
				transmission_dequeue_guid=_row[0],
				transmission_guid=_row[1],
				request_client_guid=_row[2],
				destination_client_guid=_row[3],
				row_created_datetime=datetime.strptime(_row[4], "%Y-%m-%d %H:%M:%S.%f")
			)

		return _transmission_dequeue is not None, _transmission_dequeue

	def get_next_transmission_dequeue(self, *, client_guid: str) -> TransmissionDequeue:

		_transmission_dequeue_guid = str(uuid.uuid4()).upper()
		_row_created_datetime = datetime.utcnow()

		_insert_cursor = self.__connection.cursor()
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
					(
						t.is_retry_ready = 1
					)
				)
			ORDER BY
				t.row_created_datetime
			LIMIT 1
		''', (_transmission_dequeue_guid, client_guid, _row_created_datetime))

		_is_successful, _transmission_dequeue = self.try_get_transmission_dequeue(
			transmission_dequeue_guid=_transmission_dequeue_guid
		)

		if _is_successful:

			_is_successful, _transmission = self.try_get_transmission(
				transmission_guid=_transmission_dequeue.get_transmission_guid()
			)

			if not _is_successful:
				raise Exception(f"Failed to find transmission with guid: {_transmission_dequeue.get_transmission_guid()}")
			else:
				_transmission_dequeue.set_transmission(
					transmission=_transmission
				)

				if _transmission_dequeue.get_transmission().get_is_retry_ready():
					_update_cursor = self.__connection.cursor()
					_update_cursor.execute('''
						UPDATE t
						SET
							t.is_retry_ready = NULL
						FROM transmission AS t
						WHERE
							t.transmission_guid = ?
					''', (_transmission_dequeue.get_transmission_guid(),))

		return _transmission_dequeue

	def transmission_completed(self, *, client_guid: str, transmission_dequeue_guid: str):

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

	def transmission_failed(self, *, client_guid: str, transmission_dequeue_guid: str, error_message_json_string: str):

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

	def try_get_transmission_dequeue_error_transmission_dequeue(self, *, transmission_dequeue_error_transmission_dequeue_guid: str) -> Tuple[bool, TransmissionDequeueErrorTransmissionDequeue]:

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
		if len(_rows) == 0:
			_transmission_dequeue_error_transmission_dequeue = None
		else:
			_row = _rows[0]

			_transmission_dequeue_error_transmission_dequeue = TransmissionDequeueErrorTransmissionDequeue(
				transmission_dequeue_error_transmission_dequeue_guid=_row[0],
				transmission_dequeue_error_transmission_guid=_row[1],
				request_client_guid=_row[2],
				destination_client_guid=_row[3],
				row_created_datetime=datetime.strptime(_row[4], "%Y-%m-%d %H:%M:%S.%f")
			)

		return _transmission_dequeue_error_transmission_dequeue is not None, _transmission_dequeue_error_transmission_dequeue

	def try_get_transmission_dequeue_error_transmission(self, *, transmission_dequeue_error_transmission_guid: str) -> Tuple[bool, TransmissionDequeueErrorTransmission]:

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
		if len(_rows) == 0:
			_transmission_dequeue_error_transmission = None
		else:
			_row = _rows[0]

			_transmission_dequeue_error_transmission = TransmissionDequeueErrorTransmission(
				transmission_dequeue_error_transmission_guid=_row[0],
				request_client_guid=_row[1],
				transmission_dequeue_guid=_row[2],
				error_message_json_string=_row[3],
				row_created_datetime=datetime.strptime(_row[4], "%Y-%m-%d %H:%M:%S.%f"),
				is_retry_ready=_row[5]
			)

		return _transmission_dequeue_error_transmission is not None, _transmission_dequeue_error_transmission

	def get_next_failed_transmission_dequeue(self, *, client_guid: str) -> TransmissionDequeueErrorTransmissionDequeue:

		_transmission_dequeue_error_transmission_dequeue_guid = str(uuid.uuid4()).upper()
		_row_created_datetime = datetime.utcnow()

		_insert_cursor = self.__connection.cursor()
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
			ORDER BY
				t.row_created_datetime
			LIMIT 1
		''', (_transmission_dequeue_error_transmission_dequeue_guid, client_guid, _row_created_datetime))

		_is_successful, _transmission_dequeue_error_transmission_dequeue = self.try_get_transmission_dequeue_error_transmission_dequeue(
			transmission_dequeue_error_transmission_dequeue_guid=_transmission_dequeue_error_transmission_dequeue_guid
		)

		if _is_successful:

			_is_successful, _transmission_dequeue_error_transmission = self.try_get_transmission_dequeue_error_transmission(
				transmission_dequeue_error_transmission_guid=_transmission_dequeue_error_transmission_dequeue.get_transmission_dequeue_error_transmission_guid()
			)

			if not _is_successful:
				raise Exception(f"Failed to find transmission dequeue error transmission with guid: \"{_transmission_dequeue_error_transmission_dequeue.get_transmission_dequeue_error_transmission_guid()}\".")
			else:
				_transmission_dequeue_error_transmission_dequeue.set_transmission_dequeue_error_transmission(
					transmission_dequeue_error_transmission=_transmission_dequeue_error_transmission
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

					_is_successful, _transmission = self.try_get_transmission(
						transmission_guid=_transmission_dequeue.get_transmission_guid()
					)

					if not _is_successful:
						raise Exception(
							f"Failed to find transmission with guid: \"{_transmission_dequeue.get_transmission_guid()}\".")
					else:
						_transmission_dequeue.set_transmission(
							transmission=_transmission
						)

		return _transmission_dequeue_error_transmission_dequeue

	def failed_transmission_completed(self, *, client_guid: str, transmission_dequeue_error_transmission_dequeue_guid: str, is_retry_requested: bool):

		_transmission_dequeue_error_transmission_complete_guid = str(uuid.uuid4()).upper()
		_row_created_datetime = datetime.utcnow()

		_insert_cursor = self.__connection.cursor()
		_insert_cursor.execute('''
			INSERT INTO transmission_dequeue_error_transmission_complete
			(
				transmission_dequeue_error_transmission_complete_guid,
				transmission_dequeue_error_transmission_dequeue_guid,
				request_client_guid,
				is_retry_requested,
				row_created_datetime
			)
			VALUES (?, ?, ?, ?, ?);
			
			UPDATE t
			SET
				t.is_retry_ready = 0
			FROM transmission AS t
			INNER JOIN transmission_dequeue AS td
			ON
				td.transmission_guid = t.transmission_guid
			INNER JOIN transmission_dequeue_error_transmission AS tdet
			ON
				tdet.transmission_dequeue_guid = td.transmission_dequeue_guid
			INNER JOIN transmission_dequeue_error_transmission_dequeue tdetd
			ON
				tdetd.transmission_dequeue_error_transmission_guid = tdet.transmission_dequeue_error_transmission_guid
			WHERE
				tdetd.transmission_dequeue_error_transmission_dequeue_guid = ?
				AND ? = 1
		''', (_transmission_dequeue_error_transmission_complete_guid, transmission_dequeue_error_transmission_dequeue_guid, client_guid, is_retry_requested, _row_created_datetime, transmission_dequeue_error_transmission_dequeue_guid, is_retry_requested))

	def failed_transmission_failed(self, *, client_guid: str, transmission_dequeue_error_transmission_dequeue_guid: str):

		_transmission_dequeue_error_transmission_error_guid = str(uuid.uuid4()).upper()
		_row_created_datetime = datetime.utcnow()

		_insert_cursor = self.__connection.cursor()
		_insert_cursor.execute('''
			INSERT INTO transmission_dequeue_error_transmission_error
			(
				transmission_dequeue_error_transmission_error_guid,
				transmission_dequeue_error_transmission_dequeue_guid,
				request_client_guid,
				row_created_datetime
			)
			VALUES (?, ?, ?, ?);
			
			UPDATE tdet
			SET 
				tdet.is_retry_ready = 0
			FROM transmission_dequeue_error_transmission AS tdet
			JOIN transmission_dequeue_error_transmission_dequeue tdetd
			ON
				tdetd.transmission_dequeue_error_transmission_guid = tdet.transmission_dequeue_error_transmission_guid
			WHERE
				tdetd.transmission_dequeue_error_transmission_dequeue_guid = ?
		''', (_transmission_dequeue_error_transmission_error_guid, transmission_dequeue_error_transmission_dequeue_guid, client_guid, _row_created_datetime, transmission_dequeue_error_transmission_dequeue_guid))
