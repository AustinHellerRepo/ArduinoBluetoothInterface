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


@app.get("/announce")
def receive_device_announcement(unique_id: str, purpose_id: int, request: Request):
	_is_successful = False
	_device_json = None
	try:
		_database = get_database()
		_client = _database.insert_client(
			ip_address=request.client.host
		)
		_device = _database.insert_device(
			unique_id=unique_id,
			purpose_id=purpose_id
		)
		_device_json = _device.to_json()
	except:
		traceback.print_exc()
	return {
		"is_successful": _is_successful,
		"device": _device_json
	}
