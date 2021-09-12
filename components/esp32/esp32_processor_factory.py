from socket_client_factory import SocketClientFactory, SocketClient


class Esp32Processor():

	def __init__(self, *, socket_client_factory: SocketClientFactory, accepting_connections_total: int, processing_method):

		self.__socket_client_factory = socket_client_factory
		self.__accepting_connections_total = accepting_connections_total
		self.__processing_method = processing_method

		self.__socket_client = None  # type: SocketClient

	def start(self):

		if self.__socket_client is not None:
			raise Exception(f"Cannot start without first stopping previous run.")
		else:
			self.__socket_client = self.__socket_client_factory.get_socket_client()
			self.__socket_client.start_accepting_messages(
				connections_total=self.__accepting_connections_total,
				processing_method=self.__processing_method
			)

	def stop(self):

		if self.__socket_client is None:
			raise Exception(f"Cannot stop without first starting run.")
		else:
			self.__socket_client.stop_accepting_messages()


class Esp32ProcessorFactory():

	def __init__(self, *, socket_client_factory: SocketClientFactory, accepting_connections_total: int, processing_method):

		self.__socket_client_factory = socket_client_factory
		self.__accepting_connections_total = accepting_connections_total
		self.__processing_method = processing_method

	def get_esp32_processor(self) -> Esp32Processor:

		return Esp32Processor(
			socket_client_factory=self.__socket_client_factory,
			accepting_connections_total=self.__accepting_connections_total,
			processing_method=self.__processing_method
		)
