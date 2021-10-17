from austin_heller_repo.socket import ServerSocketFactory, ServerSocket, ClientSocket, json, time, start_thread, os, get_machine_guid, get_module_from_file_path, try_mkdir
from austin_heller_repo.api_interface import ApiInterfaceFactory
import network
from src.austin_heller_repo.transmission_parser import ReceiveJsonTransmissionParser, ChangePurposeTransmissionParser
from austin_heller_repo.module import ModuleReference, ModuleMessage


class Esp32Processor():

	def __init__(self, *, host_ip_address: str, host_port: int, server_socket_factory: ServerSocketFactory, accepting_connections_total: int, wifi_settings_json_file_path: str, api_interface_factory: ApiInterfaceFactory, purpose_git_clone_directory_path: str, initial_purpose_settings_file_path: str):

		self.__host_ip_address = host_ip_address
		self.__host_port = host_port
		self.__server_socket_factory = server_socket_factory
		self.__accepting_connections_total = accepting_connections_total
		self.__wifi_settings_json_file_path = wifi_settings_json_file_path
		self.__api_interface_factory = api_interface_factory
		self.__purpose_git_clone_directory_path = purpose_git_clone_directory_path
		self.__initial_purpose_settings_file_path = initial_purpose_settings_file_path

		self.__server_socket = None  # type: ServerSocket
		self.__device_guid = None  # type: str
		self.__module_reference = None  # type: ModuleReference
		self.__processor_guid = None  # type: str

		self.__initialize()

	def __initialize(self):

		self.__device_guid = get_machine_guid()

		try_mkdir(self.__purpose_git_clone_directory_path)

		_api_interface = self.__api_interface_factory.get_api_interface()

		self.__processor_guid = _api_interface.get_uuid()["response"]["uuid"]

	def start(self):

		if self.__server_socket is not None:
			raise Exception(f"Cannot start without first stopping previous run.")
		else:

			# connect to the wifi

			with open(self.__wifi_settings_json_file_path, "r") as _wifi_settings_file_handle:
				_wifi_settings_json_string = _wifi_settings_file_handle.read()
			_wifi_settings_json = json.loads(_wifi_settings_json_string)

			if "ssid" not in _wifi_settings_json:
				_error = "\"ssid\" missing from wifi settings json file at \"" + self.__wifi_settings_json_file_path + "\""
				print(_error)
				raise Exception(_error)
			else:
				_ssid = _wifi_settings_json["ssid"]

			if "password" not in _wifi_settings_json:
				_error = "\"password\" missing from wifi settings json file at \"" + self.__wifi_settings_json_file_path + "\""
				print(_error)
				raise Exception(_error)
			else:
				_password = _wifi_settings_json["password"]

			if "connection_timeout_seconds" not in _wifi_settings_json:
				_error = "\"connection_timeout_seconds\" missing from wifi settings json file at \"" + self.__wifi_settings_json_file_path + "\""
				print(_error)
				raise Exception(_error)
			else:
				_connection_timeout_seconds = float(_wifi_settings_json["connection_timeout_seconds"])

			_sta_if = network.WLAN(network.STA_IF)
			if _sta_if.isconnected():
				_error = "Unexpectedly already connected to the wifi"
				print(_error)
				raise Exception(_error)

			_sta_if.active(True)
			_sta_if.connect(_ssid, _password)
			_current_connecting_seconds = 0.0
			_delay_connecting_seconds = 0.1
			while not _sta_if.isconnected():
				time.sleep(_delay_connecting_seconds)
				_current_connecting_seconds += _delay_connecting_seconds
				if _current_connecting_seconds >= _connection_timeout_seconds:
					_error = "Connection timed out after " + str(_current_connecting_seconds) + " second" + ("s" if _current_connecting_seconds != 1 else "")
					print(_error)
					raise Exception(_error)

			# start the listening socket

			def _send_message_method(module_message: ModuleMessage):
				_api_interface = self.__api_interface_factory.get_api_interface()
				_api_interface.send_transmission(
					queue_guid=module_message.get_queue_guid(),
					source_device_guid=module_message.get_source_device_guid(),
					source_device_instance_guid=module_message.get_source_device_instance_guid(),
					destination_device_guid=module_message.get_destination_device_guid(),
					destination_device_instance_guid=module_message.get_destination_device_instance_guid(),
					transmission_json=module_message.get_transmission_json()
				)

			def _get_devices_by_purpose_method(purpose_guid: str):
				_api_interface = self.__api_interface_factory.get_api_interface()
				_devices = _api_interface.get_available_devices(
					purpose_guid=purpose_guid
				)
				return _devices

			def _on_ready_method(purpose_guid: str) -> str:
				_api_interface = self.__api_interface_factory.get_api_interface()
				_device = _api_interface.send_device_announcement(
					device_guid=self.__device_guid,
					purpose_guid=purpose_guid,
					socket_port=self.__host_port
				)
				return _device["device"]["instance_guid"]

			def _process_client_socket(client_socket: ClientSocket):
				_header_json_string = client_socket.read()
				_header_json = json.loads(_header_json_string)
				if _header_json["type"] == "send message":
					_transmission_parser = ReceiveJsonTransmissionParser(
						module_reference=self.__module_reference
					)
				elif _header_json["type"] == "change_purpose":
					_transmission_parser = ChangePurposeTransmissionParser(
						module_reference=self.__module_reference,
						git_clone_directory_path=self.__purpose_git_clone_directory_path,
						device_guid=self.__device_guid,
						send_message_method=_send_message_method,
						get_devices_by_purpose_method=_get_devices_by_purpose_method,
						on_ready_method=_on_ready_method
					)
				client_socket.close()

			self.__server_socket = self.__server_socket_factory.get_server_socket()
			self.__server_socket.start_accepting_clients(
				host_ip_address=self.__host_ip_address,
				host_port=self.__host_port,
				on_accepted_client_method=_process_client_socket
			)

			def _waiting_for_termination_thread_method():
				while self.__server_socket.is_accepting_clients():
					time.sleep(1.0)
				self.__server_socket.close()

			_waiting_for_termination_thread = start_thread(_waiting_for_termination_thread_method)

			# load initial purpose

			with open(self.__initial_purpose_settings_file_path, "r") as _initial_purpose_settings_file_handle:
				_initial_purpose_settings_json_string = _initial_purpose_settings_file_handle.read()
			_initial_purpose_settings_json = json.loads(_initial_purpose_settings_json_string)

			if "implemented_module_git_repo_url" not in _initial_purpose_settings_json:
				_error = "\"implemented_module_git_repo_url\" missing from initial purpose settings json file at \"" + self.__initial_purpose_settings_file_path + "\""
				print(_error)
				raise Exception(_error)
			else:
				_implemented_module_git_repo_url = _initial_purpose_settings_json["implemented_module_git_repo_url"]

			_api_interface = self.__api_interface_factory.get_api_interface()

			_device_announcement_response = _api_interface.send_device_announcement(
				device_guid=self.__device_guid,
				purpose_guid=None,
				socket_port=self.__host_port
			)

			_device = _device_announcement_response["device"]

			_api_interface.change_purpose(
				queue_guid=self.__processor_guid,
				source_device_guid=self.__device_guid,
				source_device_instance_guid=_device["device_instance_guid"],
				destination_device_guid=self.__device_guid,
				destination_device_instance_guid=_device["device_instance_guid"],
				git_repository_url=_implemented_module_git_repo_url
			)

	def stop(self):

		if self.__module_reference.get() is not None:
			self.__module_reference.get().stop()


class Esp32ProcessorFactory():

	def __init__(self, *, host_ip_address: str, host_port: int, server_socket_factory: ServerSocketFactory, accepting_connections_total: int, wifi_settings_json_file_path: str, api_interface_factory: ApiInterfaceFactory, purpose_git_clone_directory_path: str, initial_purpose_settings_file_path: str):

		self.__host_ip_address = host_ip_address
		self.__host_port = host_port
		self.__server_socket_factory = server_socket_factory
		self.__accepting_connections_total = accepting_connections_total
		self.__wifi_settings_json_file_path = wifi_settings_json_file_path
		self.__api_interface_factory = api_interface_factory
		self.__purpose_git_clone_directory_path = purpose_git_clone_directory_path
		self.__initial_purpose_settings_file_path = initial_purpose_settings_file_path

	def get_esp32_processor(self) -> Esp32Processor:

		return Esp32Processor(
			host_ip_address=self.__host_ip_address,
			host_port=self.__host_port,
			server_socket_factory=self.__server_socket_factory,
			accepting_connections_total=self.__accepting_connections_total,
			wifi_settings_json_file_path=self.__wifi_settings_json_file_path,
			api_interface_factory=self.__api_interface_factory,
			purpose_git_clone_directory_path=self.__purpose_git_clone_directory_path,
			initial_purpose_settings_file_path=self.__initial_purpose_settings_file_path
		)
