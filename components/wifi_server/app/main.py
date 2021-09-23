from fastapi import FastAPI, Request
from app.database import DatabaseFactory, Database, ApiEntrypoint
import traceback
from typing import List, Tuple, Dict
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import asyncio
from pydantic import BaseModel
from austin_heller_repo.socket import ClientSocketFactory, ClientSocket
from app.dequeuer import Dequeuer


try:
	_loop = asyncio.get_running_loop()
	_loop.set_default_executor(ThreadPoolExecutor(max_workers=1))  # TODO pull from settings
except:
	pass


app = FastAPI()


__database_factory = DatabaseFactory()
__client_socket_factory = ClientSocketFactory(
	to_server_packet_bytes_length=4096,
	server_read_failed_delay_seconds=0.1
)

__dequeuer = Dequeuer(
	database_factory=__database_factory,
	client_socket_factory=__client_socket_factory,
	polling_thread_delay_seconds=60.0
)
__dequeuer.add_dequeuer()


def get_database() -> Database:
	global __database_factory
	return __database_factory.get_database()


def log_api_entrypoint(*, api_entrypoint: ApiEntrypoint, args_json: Dict, request: Request):
	try:
		_altered_json = args_json.copy()
		_altered_json["request"] = {
			"method": request.method,
			"url": {
				"query": request.url.query,
				"path": request.url.path,
				"hostname": request.url.hostname,
				"is_secure": request.url.is_secure,
				"scheme": request.url.scheme,
				"port": request.url.port
			},
			"client": {
				"host": request.client.host,
				"port": request.client.port
			},
			"headers": request.headers.items()
		}

		_database = get_database()
		_client = _database.insert_client(
			ip_address=request.client.host
		)

		# NOTE errors here could indicate that new api entry point has not been added to database
		#  check the __initialize function in the database module

		_database.insert_api_entrypoint_log(
			client_guid=_client.get_client_guid(),
			api_entrypoint=api_entrypoint,
			input_json_string=json.dumps(_altered_json)
		)
	except Exception as ex:
		_error_message = f"{str(ex)} after entry point {api_entrypoint}"
		traceback.print_exc()


@app.get("/v1/test/get")
def test_get(request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.TestGet,
		args_json={},
		request=request
	)

	_is_successful = True
	_response_json = None
	_error_message = None
	return {
		"is_successful": _is_successful,
		"response": _response_json,
		"error": _error_message
	}


@app.post("/v1/test/post")
def test_post(request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.TestPost,
		args_json={},
		request=request
	)

	_is_successful = True
	_response_json = None
	_error_message = None
	return {
		"is_successful": _is_successful,
		"response": _response_json,
		"error": _error_message
	}


class TestJsonBaseModel(BaseModel):
	test: str


@app.post("/v1/test/json")
def test_json(test_json_base_model: TestJsonBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.TestJson,
		args_json=json.loads(test_json_base_model.json()),
		request=request
	)

	_is_successful = True
	_response_json = json.loads(test_json_base_model.json())
	_error_message = None
	return {
		"is_successful": _is_successful,
		"response": _response_json,
		"error": _error_message
	}


class ReceiveDeviceAnnouncementBaseModel(BaseModel):
	device_guid: str
	purpose_guid: str
	socket_port: int


@app.post("/v1/device/announce")
def v1_receive_device_announcement(receive_device_announcement_base_model: ReceiveDeviceAnnouncementBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1ReceiveDeviceAnnouncement,
		args_json=json.loads(receive_device_announcement_base_model.json()),
		request=request
	)

	_is_successful = False
	_response_json = None
	_error_message = None

	try:
		_database = get_database()
		_client = _database.insert_client(
			ip_address=request.client.host
		)
		_device = _database.insert_device(
			device_guid=receive_device_announcement_base_model.device_guid,
			client_guid=_client.get_client_guid(),
			purpose_guid=receive_device_announcement_base_model.purpose_guid,
			socket_port=receive_device_announcement_base_model.socket_port
		)

		__dequeuer.

		_response_json = {
			"device": _device.to_json()
		}
		_is_successful = True
	except Exception as ex:
		#_error_message = str(ex)
		#traceback.print_exc()
		_error_message = traceback.format_exc()

	return {
		"is_successful": _is_successful,
		"response": _response_json,
		"error": _error_message
	}


class ListAvailableDevicesBaseModel(BaseModel):
	purpose_guid: str


@app.post("/v1/device/list")
def v1_list_available_devices(list_available_devices_base_model: ListAvailableDevicesBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1ListDevices,
		args_json=json.loads(list_available_devices_base_model.json()),
		request=request
	)

	_is_successful = False
	_response_json = None
	_error_message = None

	try:
		_database = get_database()
		_devices = _database.get_devices_by_purpose(
			purpose_guid=list_available_devices_base_model.purpose_guid
		)
		_devices_json_array = []
		for _device in _devices:
			_devices_json_array.append(_device.to_json())
		_response_json = {
			"devices": _devices_json_array
		}
		_is_successful = True
	except Exception as ex:
		_error_message = str(ex)
		traceback.print_exc()

	return {
		"is_successful": _is_successful,
		"response": _response_json,
		"error": _error_message
	}


class ReceiveDeviceTransmissionBaseModel(BaseModel):
	queue_guid: str
	source_device_guid: str
	transmission_json_string: str
	destination_device_guid: str


@app.post("/v1/transmission/enqueue")
def v1_receive_device_transmission(receive_device_transmission_base_model: ReceiveDeviceTransmissionBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1ReceiveDeviceTransmission,
		args_json=json.loads(receive_device_transmission_base_model.json()),
		request=request
	)

	_is_successful = False
	_response_json = None
	_error_message = None

	try:
		_database = get_database()
		_client = _database.insert_client(
			ip_address=request.client.host
		)
		_queue = _database.insert_queue(
			queue_guid=receive_device_transmission_base_model.queue_guid
		)
		_transmission = _database.insert_transmission(
			queue_guid=_queue.get_queue_guid(),
			source_device_guid=receive_device_transmission_base_model.source_device_guid,
			client_guid=_client.get_client_guid(),
			transmission_json_string=receive_device_transmission_base_model.transmission_json_string,
			destination_device_guid=receive_device_transmission_base_model.destination_device_guid
		)

		_responsive_dequeuers = _database.get_all_responsive_dequeuers(
			queue_guid=_transmission.get_queue_guid()
		)

		if len(_responsive_dequeuers) != 0:

			_to_dequeuer_packet_bytes_length = 4096
			_dequeuer_read_failed_delay_seconds = 0.1

			_client_socket_factory = ClientSocketFactory(
				to_server_packet_bytes_length=_to_dequeuer_packet_bytes_length,
				server_read_failed_delay_seconds=_dequeuer_read_failed_delay_seconds
			)

			for _responsive_dequeuer in _responsive_dequeuers:
				_client_socket = _client_socket_factory.get_client_socket()
				_client_socket.connect_to_server(
					ip_address=_responsive_dequeuer.get_last_known_client().get_ip_address(),
					port=_responsive_dequeuer.get_listening_port()
				)
				_client_socket.write(json.dumps({
					"queue_guid": _transmission.get_queue_guid()
				}))
				_client_socket.close()

		_response_json = {
			"transmission": _transmission.to_json()
		}
		_is_successful = True
	except Exception as ex:
		_error_message = str(ex)
		traceback.print_exc()

	return {
		"is_successful": _is_successful,
		"response": _response_json,
		"error": _error_message
	}


@app.post("/v1/uuid")
def v1_get_uuid(request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1GetUuid,
		args_json={},
		request=request
	)

	_is_successful = False
	_response_json = None
	_error_message = None

	try:
		_response_json = {
			"uuid": str(uuid.uuid4()).upper()
		}
		_is_successful = True
	except Exception as ex:
		_error_message = str(ex)
		traceback.print_exc()

	return {
		"is_successful": _is_successful,
		"response": _response_json,
		"error": _error_message
	}
