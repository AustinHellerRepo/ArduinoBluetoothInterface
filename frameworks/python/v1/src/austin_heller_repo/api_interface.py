try:
	import urequests as requests
except ImportError:
	import requests

try:
	import ujson as json
except ImportError:
	import json


class MethodTypeEnum():
	Get = 0
	Post = 1


class ApiInterface():

	def __init__(self, *, api_base_url: str):

		self.__api_base_url = api_base_url

	def _get_json_result_from_url(self, *, method_type, url: str, arguments_json_object: dict) -> dict:

		print("Trying to " + str(method_type) + " to \"" + url + "\"...")

		if method_type == MethodTypeEnum.Get:
			_response = requests.get(url, json=arguments_json_object)
		elif method_type == MethodTypeEnum.Post:
			_response = requests.post(url, json=arguments_json_object)
		else:
			raise NotImplementedError()

		if _response.status_code != 200:
			raise Exception("Unexpected status code: " + str(_response.status_code) + ": " + str(_response.reason) + ". Error: \"" + str(_response.text) + "\".")
		else:
			_json_response = _response.json()
			if "is_successful" not in _json_response:
				raise Exception("Unexpected missing key \"is_successful\": " + str(_json_response))
			elif "response" not in _json_response:
				raise Exception("Unexpected missing key \"response\": " + str(_json_response))
			elif "error" not in _json_response:
				raise Exception("Unexpected missing key \"error\": " + str(_json_response))
			else:
				_is_successful = _json_response["is_successful"]
				_response_value = _json_response["response"]
				_error = _json_response["error"]
				if not _is_successful:
					raise Exception("Error from messaging system: \"" + str(_error) + "\".")
				else:
					return _response_value

	def _get_formatted_url(self, *, url_part: str) -> str:
		return self.__api_base_url + url_part

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

	def send_transmission(self, *, queue_guid: str, source_device_guid: str, source_device_instance_guid: str, destination_device_guid: str, destination_device_instance_guid: str, transmission_json: dict) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/transmission/enqueue"
			),
			arguments_json_object={
				"queue_guid": queue_guid,
				"source_device_guid": source_device_guid,
				"source_device_instance_guid": source_device_instance_guid,
				"destination_device_guid": destination_device_guid,
				"destination_device_instance_guid": destination_device_instance_guid,
				"transmission_json_string": json.dumps(transmission_json)
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

	def change_purpose(self, *, queue_guid: str, source_device_guid: str, source_device_instance_guid: str, destination_device_guid: str, destination_device_instance_guid: str, git_repository_url: str) -> dict:

		return self._get_json_result_from_url(
			method_type=MethodTypeEnum.Post,
			url=self._get_formatted_url(
				url_part="/v1/transmission/enqueue"
			),
			arguments_json_object={
				"queue_guid": queue_guid,
				"source_device_guid": source_device_guid,
				"source_device_instance_guid": source_device_instance_guid,
				"destination_device_guid": destination_device_guid,
				"destination_device_instance_guid": destination_device_instance_guid,
				"git_repository_url": git_repository_url
			}
		)


class ApiInterfaceFactory():

	def __init__(self, *, api_base_url: str):

		self.__api_base_url = api_base_url

	def get_api_interface(self) -> ApiInterface:
		return ApiInterface(
			api_base_url=self.__api_base_url
		)
