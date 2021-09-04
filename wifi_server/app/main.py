from fastapi import FastAPI, Request
from app.database import Database, ApiEntrypoint
import traceback
from typing import List, Tuple, Dict
import json
import uuid

app = FastAPI()


__singleton_database = None


def get_database() -> Database:
	global __singleton_database
	if __singleton_database is None:
		__singleton_database = Database()
	return __singleton_database


def log_api_entrypoint(*, api_entrypoint: ApiEntrypoint, args_json: Dict, request: Request):
	try:
		args_json["request"] = {
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
			input_json_string=json.dumps(args_json)
		)
	except Exception as ex:
		_error_message = f"{str(ex)} after entry point {api_entrypoint}"
		traceback.print_exc()


@app.get("/")
def test_root(request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.TestRoot,
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


@app.post("/v1/device/announce")
def v1_receive_device_announcement(device_guid: str, purpose_guid: str, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1ReceiveDeviceAnnouncement,
		args_json={
			"device_guid": device_guid,
			"purpose_guid": purpose_guid,
		},
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
			device_guid=device_guid,
			client_guid=_client.get_client_guid(),
			purpose_guid=purpose_guid
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


@app.post("/v1/device/list")
def v1_list_available_devices(purpose_guid: str, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1ListDevices,
		args_json={
			"purpose_guid": purpose_guid
		},
		request=request
	)

	_is_successful = False
	_response_json = None
	_error_message = None

	try:
		_database = get_database()
		_devices = _database.get_devices_by_purpose(
			purpose_guid=purpose_guid
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


@app.post("/v1/dequeuer/announce")
def v1_receive_dequeuer_announcement(dequeuer_guid: str, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1ReceiveDequeuerAnnouncement,
		args_json={
			"dequeuer_guid": dequeuer_guid
		},
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
			dequeuer_guid=dequeuer_guid,
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


@app.post("/v1/reporter/announce")
def v1_receive_reporter_announcement(reporter_guid: str, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1ReceiveReporterAnnouncement,
		args_json={
			"reporter_guid": reporter_guid
		},
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
			reporter_guid=reporter_guid,
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


@app.post("/v1/transmission/enqueue")
def v1_receive_device_transmission(queue_guid: str, source_device_guid: str, transmission_json_string: str, destination_device_guid: str, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1ReceiveDeviceTransmission,
		args_json={
			"queue_guid": queue_guid,
			"source_device_guid": source_device_guid,
			"transmission_json_string": transmission_json_string,
			"destination_device_guid": destination_device_guid
		},
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
			queue_guid=queue_guid
		)
		_transmission = _database.insert_transmission(
			queue_guid=_queue.get_queue_guid(),
			source_device_guid=source_device_guid,
			client_guid=_client.get_client_guid(),
			transmission_json_string=transmission_json_string,
			destination_device_guid=destination_device_guid
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


@app.post("/v1/transmission/dequeue")
def v1_dequeue_next_transmission(dequeuer_guid: str, queue_guid: str, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1DequeueNextTransmission,
		args_json={
			"dequeuer_guid": dequeuer_guid,
			"queue_guid": queue_guid
		},
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
			queue_guid=queue_guid
		)
		_transmission_dequeue = _database.get_next_transmission_dequeue(
			dequeuer_guid=dequeuer_guid,
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


@app.post("/v1/transmission/complete")
def v1_complete_transmission(transmission_dequeue_guid: str, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1CompleteTransmission,
		args_json={
			"transmission_dequeue_guid": transmission_dequeue_guid
		},
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
			transmission_dequeue_guid=transmission_dequeue_guid
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


@app.post("/v1/transmission/failure")
def v1_failed_transmission(transmission_dequeue_guid: str, error_message_json_string: str, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1FailedTransmission,
		args_json={
			"transmission_dequeue_guid": transmission_dequeue_guid,
			"error_message_json_string": error_message_json_string
		},
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
			transmission_dequeue_guid=transmission_dequeue_guid,
			error_message_json_string=error_message_json_string
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


@app.post("/v1/failure/dequeue")
def v1_dequeue_failure_transmission(reporter_guid: str, queue_guid: str, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1DequeueFailureTransmission,
		args_json={
			"reporter_guid": reporter_guid,
			"queue_guid": queue_guid
		},
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
			queue_guid=queue_guid
		)
		_transmission_dequeue_error_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
			reporter_guid=reporter_guid,
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


@app.post("/v1/failure/complete")
def v1_complete_failure_transmission(transmission_dequeue_error_transmission_dequeue_guid: str, is_retry_requested: bool, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1CompleteFailureTransmission,
		args_json={
			"transmission_dequeue_error_transmission_dequeue_guid": transmission_dequeue_error_transmission_dequeue_guid,
			"is_retry_requested": is_retry_requested
		},
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
			transmission_dequeue_error_transmission_dequeue_guid=transmission_dequeue_error_transmission_dequeue_guid,
			is_retry_requested=is_retry_requested
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


@app.post("/v1/failure/failure")
def v1_failed_failure_transmission(transmission_dequeue_error_transmission_dequeue_guid: str, error_message_json_string: str, request: Request):

	log_api_entrypoint(
		api_entrypoint=ApiEntrypoint.V1FailedFailureTransmission,
		args_json={
			"transmission_dequeue_error_transmission_dequeue_guid": transmission_dequeue_error_transmission_dequeue_guid,
			"error_message_json_string": error_message_json_string
		},
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
			transmission_dequeue_error_transmission_dequeue_guid=transmission_dequeue_error_transmission_dequeue_guid,
			error_message_json_string=error_message_json_string
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
