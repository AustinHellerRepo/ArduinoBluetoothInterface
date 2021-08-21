from fastapi import FastAPI, Request
from app.database import Database
import traceback

app = FastAPI()


__singleton_database = None


def get_database() -> Database:
	global __singleton_database
	if __singleton_database is None:
		__singleton_database = Database()
	return __singleton_database


@app.get("/")
def test_root():
	_is_successful = True
	_response_json = None
	_error_message = None
	return {
		"is_successful": _is_successful,
		"response": _response_json,
		"error": _error_message
	}


@app.post("/v1/device/announce")
def receive_device_announcement(device_guid: str, purpose_guid: str, request: Request):

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


@app.post("/v1/transmission/enqueue")
def receive_device_transmission(source_device_guid: str, transmission_json_string: str, destination_device_guid: str, request: Request):

	_is_successful = False
	_response_json = None
	_error_message = None

	try:
		_database = get_database()
		_client = _database.insert_client(
			ip_address=request.client.host
		)
		_transmission = _database.insert_transmission(
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
def dequeue_next_transmission(request: Request):

	_is_successful = False
	_response_json = None
	_error_message = None

	try:
		_database = get_database()
		_client = _database.insert_client(
			ip_address=request.client.host
		)
		_transmission_dequeue = _database.get_next_transmission_dequeue(
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
def complete_transmission(transmission_dequeue_guid: str, request: Request):

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
def failed_transmission(transmission_dequeue_guid: str, error_message_json_string: str, request: Request):

	_is_successful = False
	_response_json = None
	_error_message = None

	try:
		_database = get_database()
		_client = _database.insert_client(
			ip_address=request.client.host
		)
		_database.transmission_failed(
			client_guid=_client.get_client_guid(),
			transmission_dequeue_guid=transmission_dequeue_guid,
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


@app.post("/v1/failure/dequeue")
def dequeue_failure_transmission(request: Request):

	_is_successful = False
	_response_json = None
	_error_message = None

	try:
		_database = get_database()
		_client = _database.insert_client(
			ip_address=request.client.host
		)
		_transmission_dequeue = _database.get_next_failed_transmission_dequeue(
			client_guid=_client.get_client_guid()
		)
		if _transmission_dequeue is None:
			_transmission_dequeue_json = None
		else:
			_transmission_dequeue_json = _transmission_dequeue.to_json()
		_response_json = {
			"failure_transmission_dequeue": _transmission_dequeue_json
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
def complete_failure_transmission(transmission_dequeue_error_transmission_dequeue_guid: str, is_retry_requested: bool, request: Request):

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
def failed_failure_transmission(transmission_dequeue_error_transmission_dequeue_guid: str, error_message_json_string: str, request: Request):

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
