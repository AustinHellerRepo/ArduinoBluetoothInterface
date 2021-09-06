from fastapi import FastAPI, Request
from app.database import Database, ApiEntrypoint
import traceback
from typing import List, Tuple, Dict
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import asyncio
from pydantic import BaseModel


try:
	_loop = asyncio.get_running_loop()
	_loop.set_default_executor(ThreadPoolExecutor(max_workers=1))  # TODO pull from settings
except:
	pass


app = FastAPI()


__singleton_database = None


def get_database() -> Database:
	global __singleton_database
	if __singleton_database is None:
		__singleton_database = Database()
	return __singleton_database


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
			purpose_guid=receive_device_announcement_base_model.purpose_guid
		)
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


class ReceiveDequeuerAnnouncementBaseModel(BaseModel):
	dequeuer_guid: str
	# TODO add is_informed_of_enqueue: bool


@app.post("/v1/dequeuer/announce")
def v1_receive_dequeuer_announcement(receive_dequeuer_announcement_base_model: ReceiveDequeuerAnnouncementBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1ReceiveDequeuerAnnouncement,
		args_json=json.loads(receive_dequeuer_announcement_base_model.json()),
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
		_dequeuer = _database.insert_dequeuer(
			dequeuer_guid=receive_dequeuer_announcement_base_model.dequeuer_guid,
			is_informed_of_enqueue=False,
			client_guid=_client.get_client_guid()
		)
		_response_json = {
			"dequeuer": _dequeuer.to_json()
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


class ReceiveReporterAnnouncementBaseModel(BaseModel):
	reporter_guid: str


@app.post("/v1/reporter/announce")
def v1_receive_reporter_announcement(receive_reporter_announcement_base_model: ReceiveReporterAnnouncementBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1ReceiveReporterAnnouncement,
		args_json=json.loads(receive_reporter_announcement_base_model.json()),
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
		_reporter = _database.insert_reporter(
			reporter_guid=receive_reporter_announcement_base_model.reporter_guid,
			is_informed_of_enqueue=False,
			client_guid=_client.get_client_guid()
		)
		_response_json = {
			"reporter": _reporter.to_json()
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


class DequeueNextTransmissionBaseModel(BaseModel):
	dequeuer_guid: str
	queue_guid: str


@app.post("/v1/transmission/dequeue")
def v1_dequeue_next_transmission(dequeue_next_transmission_base_model: DequeueNextTransmissionBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1DequeueNextTransmission,
		args_json=json.loads(dequeue_next_transmission_base_model.json()),
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
			queue_guid=dequeue_next_transmission_base_model.queue_guid
		)
		_transmission_dequeue = _database.get_next_transmission_dequeue(
			dequeuer_guid=dequeue_next_transmission_base_model.dequeuer_guid,
			queue_guid=_queue.get_queue_guid(),
			client_guid=_client.get_client_guid()
		)
		if _transmission_dequeue is None:
			_transmission_dequeue_json = None
		else:
			_transmission_dequeue_json = _transmission_dequeue.to_json()
		_response_json = {
			"transmission_dequeue": _transmission_dequeue_json
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


class CompleteTransmissionBaseModel(BaseModel):
	transmission_dequeue_guid: str


@app.post("/v1/transmission/complete")
def v1_complete_transmission(complete_transmission_base_model: CompleteTransmissionBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1CompleteTransmission,
		args_json=json.loads(complete_transmission_base_model.json()),
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
		_transmission = _database.transmission_completed(
			client_guid=_client.get_client_guid(),
			transmission_dequeue_guid=complete_transmission_base_model.transmission_dequeue_guid
		)
		if _transmission is None:
			_transmission_json = None
		else:
			_transmission_json = _transmission.to_json()
		_response_json = {
			"transmission": _transmission_json
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


class FailedTransmissionBaseModel(BaseModel):
	transmission_dequeue_guid: str
	error_message_json_string: str


@app.post("/v1/transmission/failure")
def v1_failed_transmission(failed_transmission_base_model: FailedTransmissionBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1FailedTransmission,
		args_json=json.loads(failed_transmission_base_model.json()),
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
		_transmission_dequeue_error_transmission = _database.transmission_failed(
			client_guid=_client.get_client_guid(),
			transmission_dequeue_guid=failed_transmission_base_model.transmission_dequeue_guid,
			error_message_json_string=failed_transmission_base_model.error_message_json_string
		)
		_response_json = {
			"transmission_dequeue_error_transmission": _transmission_dequeue_error_transmission.to_json()
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


class DequeueFailureTransmissionBaseModel(BaseModel):
	reporter_guid: str
	queue_guid: str


@app.post("/v1/failure/dequeue")
def v1_dequeue_failure_transmission(dequeue_failure_transmission_base_model: DequeueFailureTransmissionBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1DequeueFailureTransmission,
		args_json=json.loads(dequeue_failure_transmission_base_model.json()),
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
			queue_guid=dequeue_failure_transmission_base_model.queue_guid
		)
		_transmission_dequeue_error_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
			reporter_guid=dequeue_failure_transmission_base_model.reporter_guid,
			queue_guid=_queue.get_queue_guid(),
			client_guid=_client.get_client_guid()
		)
		if _transmission_dequeue_error_transmission_dequeue is None:
			_transmission_dequeue_error_transmission_dequeue_json = None
		else:
			_transmission_dequeue_error_transmission_dequeue_json = _transmission_dequeue_error_transmission_dequeue.to_json()
		_response_json = {
			"transmission_dequeue_error_transmission_dequeue": _transmission_dequeue_error_transmission_dequeue_json
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


class CompleteFailureTransmissionBaseModel(BaseModel):
	transmission_dequeue_error_transmission_dequeue_guid: str
	is_retry_requested: bool


@app.post("/v1/failure/complete")
def v1_complete_failure_transmission(complete_failure_transmission_base_model: CompleteFailureTransmissionBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1CompleteFailureTransmission,
		args_json=json.loads(complete_failure_transmission_base_model.json()),
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
		_database.failed_transmission_completed(
			client_guid=_client.get_client_guid(),
			transmission_dequeue_error_transmission_dequeue_guid=complete_failure_transmission_base_model.transmission_dequeue_error_transmission_dequeue_guid,
			is_retry_requested=complete_failure_transmission_base_model.is_retry_requested
		)
		_is_successful = True
	except Exception as ex:
		_error_message = str(ex)
		traceback.print_exc()

	return {
		"is_successful": _is_successful,
		"response": _response_json,
		"error": _error_message
	}


class FailedFailureTransmissionBaseModel(BaseModel):
	transmission_dequeue_error_transmission_dequeue_guid: str
	error_message_json_string: str


@app.post("/v1/failure/failure")
def v1_failed_failure_transmission(failed_failure_transmission_base_model: FailedFailureTransmissionBaseModel, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1FailedFailureTransmission,
		args_json=json.loads(failed_failure_transmission_base_model.json()),
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
		_database.failed_transmission_failed(
			client_guid=_client.get_client_guid(),
			transmission_dequeue_error_transmission_dequeue_guid=failed_failure_transmission_base_model.transmission_dequeue_error_transmission_dequeue_guid,
			error_message_json_string=failed_failure_transmission_base_model.error_message_json_string
		)
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
