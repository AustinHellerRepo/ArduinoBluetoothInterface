from austin_heller_repo.socket_client_factory import ServerSocketFactory, ServerSocket, ClientSocket
from austin_heller_repo.api_interface import ApiInterfaceFactory


class Esp32Processor():

	def __init__(self, *, server_socket_factory: ServerSocketFactory, accepting_connections_total: int, processing_method):

		self.__server_socket_factory = server_socket_factory
		self.__accepting_connections_total = accepting_connections_total
		self.__processing_method = processing_method

		self.__server_socket = None  # type: ServerSocket

	def start(self):

		if self.__server_socket is not None:
			raise Exception(f"Cannot start without first stopping previous run.")
		else:
			self.__server_socket = self.__server_socket_factory.get_server_socket()
			self.__server_socket.start_accepting_clients(
				on_accepted_client_method=self.__processing_method
			)

	def stop(self):

		if self.__server_socket is None:
			raise Exception(f"Cannot stop without first starting run.")
		else:
			self.__server_socket.stop_accepting_clients()


class Esp32ProcessorFactory():

	def __init__(self, *, server_socket_factory: ServerSocketFactory, accepting_connections_total: int, processing_method):

		self.__server_socket_factory = server_socket_factory
		self.__accepting_connections_total = accepting_connections_total
		self.__processing_method = processing_method

	def get_esp32_processor(self) -> Esp32Processor:

		return Esp32Processor(
			server_socket_factory=self.__server_socket_factory,
			accepting_connections_total=self.__accepting_connections_total,
			processing_method=self.__processing_method
		)
