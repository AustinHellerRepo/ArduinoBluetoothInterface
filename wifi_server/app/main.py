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
	return {"is_successful": True}


@app.post("/announce")
def receive_device_announcement(device_guid: str, purpose_id: int, request: Request):

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
			purpose_id=purpose_id
		)
		_response_json = {
			"device": _device.to_json()
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


@app.post("/transmit")
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


@app.post("/dequeue")
def dequeue_next_transmission(request: Request):

	_is_successful = False
	_response_json = None
	_error_message = None

	try:
		_database = get_database()
		_client = _database.insert_client(
			ip_address=request.client.host
		)
		_transmission = _database.get_next_transmission(
			client_guid=_client.get_client_guid()
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
