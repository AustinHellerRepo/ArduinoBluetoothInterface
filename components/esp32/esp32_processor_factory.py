from austin_heller_repo.socket_client_factory import ServerSocketFactory, ServerSocket, ClientSocket, json
from austin_heller_repo.api_interface import ApiInterfaceFactory


class Esp32Processor():

	def __init__(self, *, server_socket_factory: ServerSocketFactory, accepting_connections_total: int):

		self.__server_socket_factory = server_socket_factory
		self.__accepting_connections_total = accepting_connections_total

		self.__server_socket = None  # type: ServerSocket

	def start(self):

		if self.__server_socket is not None:
			raise Exception(f"Cannot start without first stopping previous run.")
		else:

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

	def stop(self):

		if self.__server_socket is None:
			raise Exception(f"Cannot stop without first starting run.")
		else:
			self.__server_socket.stop_accepting_clients()


class Esp32ProcessorFactory():

	def __init__(self, *, server_socket_factory: ServerSocketFactory, accepting_connections_total: int):

		self.__server_socket_factory = server_socket_factory
		self.__accepting_connections_total = accepting_connections_total

	def get_esp32_processor(self) -> Esp32Processor:

		return Esp32Processor(
			server_socket_factory=self.__server_socket_factory,
			accepting_connections_total=self.__accepting_connections_total
		)
