from austin_heller_repo.socket_client_factory import ServerSocketFactory, ServerSocket, ClientSocket, json, time, start_thread, os
from austin_heller_repo.api_interface import ApiInterfaceFactory
import network


class Esp32Processor():

	def __init__(self, *, server_socket_factory: ServerSocketFactory, accepting_connections_total: int, wifi_settings_json_file_path: str):

		self.__server_socket_factory = server_socket_factory
		self.__accepting_connections_total = accepting_connections_total
		self.__wifi_settings_json_file_path = wifi_settings_json_file_path

		self.__server_socket = None  # type: ServerSocket

	def start(self):

		if self.__server_socket is not None:
			raise Exception(f"Cannot start without first stopping previous run.")
		else:

			# connect to the wifi

			if os.path.exists(self.__wifi_settings_json_file_path):
				_error = "Failed to find wifi settings file at path \"" + self.__wifi_settings_json_file_path + "\""
				print(_error)
				raise Exception(_error)

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
				_connection_timeout_seconds = _wifi_settings_json["connection_timeout_seconds"]

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

			def _process_dequeuer_routed_json(*, routed_json: dict):
				print(f"_process_dequeuer_routed_json: routed_json: {routed_json}")

			def _process_reporter_routed_json(*, routed_json: dict):
				print(f"_process_reporter_routed_json: routed_json: {routed_json}")

			def _process_client_socket(client_socket: ClientSocket):
				_source_json_string = client_socket.read()
				_source_json = json.loads(_source_json_string)
				if _source_json["router_type"] == "dequeuer":
					_process_dequeuer_routed_json(
						routed_json=_source_json["router_data"]
					)
				elif _source_json["router_type"] == "reporter":
					_process_reporter_routed_json(
						routed_json=_source_json["router_data"]
					)
				client_socket.close()

			self.__server_socket = self.__server_socket_factory.get_server_socket()
			self.__server_socket.start_accepting_clients(
				on_accepted_client_method=_process_client_socket
			)

			def _waiting_for_termination_thread_method():
				while self.__server_socket.is_accepting_clients():
					time.sleep(1.0)
				self.__server_socket.close()

			_waiting_for_termination_thread = start_thread(_waiting_for_termination_thread_method)


class Esp32ProcessorFactory():

	def __init__(self, *, server_socket_factory: ServerSocketFactory, accepting_connections_total: int, wifi_settings_json_file_path: str):

		self.__server_socket_factory = server_socket_factory
		self.__accepting_connections_total = accepting_connections_total
		self.__wifi_settings_json_file_path = wifi_settings_json_file_path

	def get_esp32_processor(self) -> Esp32Processor:

		return Esp32Processor(
			server_socket_factory=self.__server_socket_factory,
			accepting_connections_total=self.__accepting_connections_total
		)
