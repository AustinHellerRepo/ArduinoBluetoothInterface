from __future__ import annotations
from enum import Enum, auto

try:
	import urequests as requests
except ImportError:
	import requests

try:
	import ujson as json
except ImportError:
	import json


class MethodTypeEnum(Enum):

	Get = auto(),
	Post = auto()


class ApiInterface():

	def __init__(self, *, api_base_url: str):

		self.__api_base_url = api_base_url

	def _get_json_result_from_url(self, *, method_type: MethodTypeEnum, url: str, arguments_json_object: dict) -> dict:

		print(f"Trying to {method_type} to \"{url}\"...")

		if method_type == MethodTypeEnum.Get:
			_response = requests.get(url, json=arguments_json_object)
		elif method_type == MethodTypeEnum.Post:
			_response = requests.post(url, json=arguments_json_object)
		else:
			raise NotImplementedError()

		if _response.status_code != 200:
			raise Exception(f"Unexpected status code: {_response.status_code}: {_response.reason}. Error: \"{_response.text}\".")
		else:
			_json_response = _response.json()
			if "is_successful" not in _json_response:
				raise Exception(f"Unexpected missing key \"is_successful\": {_json_response}")
			elif "response" not in _json_response:
				raise Exception(f"Unexpected missing key \"response\": {_json_response}")
			elif "error" not in _json_response:
				raise Exception(f"Unexpected missing key \"error\": {_json_response}")
			else:
				_is_successful = _json_response["is_successful"]
				_response_value = _json_response["response"]
				_error = _json_response["error"]
				if not _is_successful:
					raise Exception(f"Error from messaging system: \"{_error}\".")
				else:
					return _response_value

	def _get_formatted_url(self, *, url_part: str) -> str:
		return f"{self.__api_base_url}{url_part}"

	def test_get(self) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Get,
			url=self._get_formatted_url(
				url_part="/v1/test/get"
			),
			arguments_json_object={}
		)

	def test_post(self) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/test/post"
			),
			arguments_json_object={}
		)

	def test_json(self, *, json_object: dict) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/test/json"
			),
			arguments_json_object=json_object
		)

	def send_device_announcement(self, *, device_guid: str, purpose_guid: str, socket_port: int) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/device/announce"
			),
			arguments_json_object={
				"device_guid": device_guid,
				"purpose_guid": purpose_guid,
				"socket_port": socket_port
			}
		)

	def get_available_devices(self, *, purpose_guid: str) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/device/list"
			),
			arguments_json_object={
				"purpose_guid": purpose_guid
			}
		)

	def send_dequeuer_announcement(self, *, dequeuer_guid: str) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/dequeuer/announce"
			),
			arguments_json_object={
				"dequeuer_guid": dequeuer_guid
			}
		)

	def send_reporter_announcement(self, *, reporter_guid: str) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/reporter/announce"
			),
			arguments_json_object={
				"reporter_guid": reporter_guid
			}
		)

	def send_transmission(self, *, queue_guid: str, source_device_guid: str, transmission_json: dict, destination_device_guid: str) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/transmission/enqueue"
			),
			arguments_json_object={
				"queue_guid": queue_guid,
				"source_device_guid": source_device_guid,
				"transmission_json_string": json.dumps(transmission_json),
				"destination_device_guid": destination_device_guid
			}
		)

	def dequeue_next_transmission(self, *, dequeuer_guid: str, queue_guid: str) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/transmission/dequeue"
			),
			arguments_json_object={
				"dequeuer_guid": dequeuer_guid,
				"queue_guid": queue_guid
			}
		)

	def update_transmission_as_completed(self, *, transmission_dequeue_guid: str) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/transmission/complete"
			),
			arguments_json_object={
				"transmission_dequeue_guid": transmission_dequeue_guid
			}
		)

	def update_transmission_as_failed(self, *, transmission_dequeue_guid: str, error_message_json: dict) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/transmission/failure"
			),
			arguments_json_object={
				"transmission_dequeue_guid": transmission_dequeue_guid,
				"error_message_json_string": json.dumps(error_message_json)
			}
		)

	def dequeue_next_failed_transmission(self, *, reporter_guid: str, queue_guid: str) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/failure/dequeue"
			),
			arguments_json_object={
				"reporter_guid": reporter_guid,
				"queue_guid": queue_guid
			}
		)

	def update_failed_transmission_as_completed(self, *, transmission_dequeue_error_transmission_dequeue_guid: str, is_retry_requested: bool) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/failure/complete"
			),
			arguments_json_object={
				"transmission_dequeue_error_transmission_dequeue_guid": transmission_dequeue_error_transmission_dequeue_guid,
				"is_retry_requested": is_retry_requested
			}
		)

	def update_failed_transmission_as_failed(self, *, transmission_dequeue_error_transmission_dequeue_guid: str, error_message_json: dict) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/failure/failure"
			),
			arguments_json_object={
				"transmission_dequeue_error_transmission_dequeue_guid": transmission_dequeue_error_transmission_dequeue_guid,
				"error_message_json_string": json.dumps(error_message_json)
			}
		)

	def get_uuid(self) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/uuid"
			),
			arguments_json_object={}
		)


class ApiInterfaceFactory():

	def __init__(self, *, api_base_url: str):

		self.__api_base_url = api_base_url

	def get_api_interface(self) -> ApiInterface:
		return ApiInterface(
			api_base_url=self.__api_base_url
		)
