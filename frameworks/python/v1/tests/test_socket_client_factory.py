from __future__ import annotations
from src.socket_client_factory import ServerSocketFactory, ServerSocket, ClientSocket, ClientSocketFactory
import unittest
import time
from datetime import datetime
import threading


_port = 28775


class SocketClientFactoryTest(unittest.TestCase):

	def test_initialize_socket_client_0(self):

		def _on_accepted_client_method(client_socket: ClientSocket):
			raise Exception(f"Unexpected client found")

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			on_accepted_client_method=_on_accepted_client_method
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)

	def test_start_server_socket_0(self):
		# start server socket and stop
		def _on_accepted_client_method(client_socket: ClientSocket):
			raise Exception(f"Unexpected client found")

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			on_accepted_client_method=_on_accepted_client_method
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_messages(
			connections_total=1,
			accept_timeout_seconds=0.2
		)
		_server_socket.stop_accepting_messages()

	def test_connect_sockets_0(self):
		# create accepting socket and transmitting socket
		def _on_accepted_client_method(client_socket: ClientSocket):
			print(f"Connected to client: {client_socket}")
			client_socket.close()

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			on_accepted_client_method=_on_accepted_client_method
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_messages(
			connections_total=1,
			accept_timeout_seconds=0.2
		)
		time.sleep(1)
		_client_socket_factory = ClientSocketFactory(
			ip_address="0.0.0.0",
			port=_port
		)
		self.assertIsNotNone(_client_socket_factory)
		_client_socket = _client_socket_factory.get_client_socket()
		self.assertIsNotNone(_client_socket)
		_client_socket.close()
		_server_socket.stop_accepting_messages()

	def test_connect_sockets_1(self):
		# create accepting socket and multiple client sockets

		_clients_total = 10

		def _on_accepted_client_method(client_socket: ClientSocket):
			print(f"Connected to client: {client_socket}")
			client_socket.close()

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			on_accepted_client_method=_on_accepted_client_method
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_messages(
			connections_total=_clients_total,
			accept_timeout_seconds=0.2
		)
		time.sleep(1)
		_client_socket_factory = ClientSocketFactory(
			ip_address="0.0.0.0",
			port=_port
		)
		self.assertIsNotNone(_client_socket_factory)
		_client_sockets = []
		for _client_index in range(_clients_total):
			_client_socket = _client_socket_factory.get_client_socket()
			self.assertIsNotNone(_client_socket)
			_client_sockets.append(_client_socket)
		for _client_index in range(_clients_total):
			_client_socket = _client_sockets[_client_index]
			_client_socket.close()
		_server_socket.stop_accepting_messages()

	def test_connect_sockets_2(self):
		# create accepting socket and multiple client sockets but one too many

		_clients_total = 1

		_accepted_client_index = 0
		def _on_accepted_client_method(client_socket: ClientSocket):
			nonlocal _accepted_client_index
			print(f"{_accepted_client_index}: Connected to client at time {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')}: {client_socket}")
			_accepted_client_index += 1
			time.sleep(1)
			client_socket.close()

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			on_accepted_client_method=_on_accepted_client_method
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_messages(
			connections_total=_clients_total,
			accept_timeout_seconds=30
		)
		time.sleep(1)
		_client_socket_factory = ClientSocketFactory(
			ip_address="0.0.0.0",
			port=_port
		)
		self.assertIsNotNone(_client_socket_factory)
		_client_sockets = []
		_client_sockets_threads = []
		_client_sockets_semaphore = threading.Semaphore()

		def _create_client():
			nonlocal _client_sockets_semaphore
			try:
				_client_socket = _client_socket_factory.get_client_socket()
				self.assertIsNotNone(_client_socket)
				_client_sockets_semaphore.acquire()
				_client_sockets.append(_client_socket)
				_client_sockets_semaphore.release()
			except Exception as ex:
				print(f"ex: {ex}")
		for _client_index in range(_clients_total * 100):
			_client_sockets_thread = threading.Thread(target=_create_client)
			_client_sockets_threads.append(_client_sockets_thread)
		for _client_sockets_thread in _client_sockets_threads:
			_client_sockets_thread.start()
		for _client_sockets_thread in _client_sockets_threads:
			_client_sockets_thread.join()
		for _client_index in range(len(_client_sockets)):
			_client_socket = _client_sockets[_client_index]
			_client_socket.close()
		_server_socket.stop_accepting_messages()
