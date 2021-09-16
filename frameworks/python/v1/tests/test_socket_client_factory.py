from __future__ import annotations
from src.austin_heller_repo.socket_client_factory import ServerSocketFactory, ClientSocket, ClientSocketFactory, Semaphore, get_machine_guid
import unittest
import time
from datetime import datetime
import threading
from typing import List

_port = 28776


class SocketClientFactoryTest(unittest.TestCase):

	def test_initialize_socket_client_0(self):

		_to_client_packet_bytes_length = 4

		def _on_accepted_client_method(client_socket: ClientSocket):
			raise Exception(f"Unexpected client found")

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_client_packet_bytes_length=_to_client_packet_bytes_length,
			listening_limit_total=1,
			accept_timeout_seconds=0.2,
			client_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)

	def test_start_server_socket_0(self):
		# start server socket and stop

		_to_client_packet_bytes_length = 4

		def _on_accepted_client_method(client_socket: ClientSocket):
			raise Exception(f"Unexpected client found")

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_client_packet_bytes_length=_to_client_packet_bytes_length,
			listening_limit_total=1,
			accept_timeout_seconds=0.2,
			client_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_clients(
			on_accepted_client_method=_on_accepted_client_method
		)
		_server_socket.stop_accepting_clients()

	def test_connect_sockets_0(self):
		# create accepting socket and transmitting socket

		_to_client_packet_bytes_length = 4
		_to_server_packet_bytes_length = 4

		def _on_accepted_client_method(client_socket: ClientSocket):
			print(f"Connected to client: {client_socket}")
			client_socket.close()

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_client_packet_bytes_length=_to_client_packet_bytes_length,
			listening_limit_total=1,
			accept_timeout_seconds=0.2,
			client_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_clients(
			on_accepted_client_method=_on_accepted_client_method
		)
		time.sleep(1)
		_client_socket_factory = ClientSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_server_packet_bytes_length=_to_server_packet_bytes_length,
			server_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_client_socket_factory)
		_client_socket = _client_socket_factory.get_client_socket()
		self.assertIsNotNone(_client_socket)
		_client_socket.close()
		_server_socket.stop_accepting_clients()
		_server_socket.close()

	def test_connect_sockets_1(self):
		# create accepting socket and multiple client sockets

		_to_client_packet_bytes_length = 4
		_to_server_packet_bytes_length = 4
		_clients_total = 10

		def _on_accepted_client_method(client_socket: ClientSocket):
			print(f"Connected to client: {client_socket}")
			client_socket.close()

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_client_packet_bytes_length=_to_client_packet_bytes_length,
			listening_limit_total=_clients_total,
			accept_timeout_seconds=0.2,
			client_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_clients(
			on_accepted_client_method=_on_accepted_client_method
		)
		time.sleep(1)
		_client_socket_factory = ClientSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_server_packet_bytes_length=_to_server_packet_bytes_length,
			server_read_failed_delay_seconds=0.1
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
		_server_socket.stop_accepting_clients()
		_server_socket.close()

	def test_connect_sockets_2(self):
		# create accepting socket and multiple client sockets but one too many

		_to_client_packet_bytes_length = 4
		_to_server_packet_bytes_length = 4
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
			to_client_packet_bytes_length=_to_client_packet_bytes_length,
			listening_limit_total=_clients_total,
			accept_timeout_seconds=30,
			client_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_clients(
			on_accepted_client_method=_on_accepted_client_method
		)
		time.sleep(1)
		_client_socket_factory = ClientSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_server_packet_bytes_length=_to_server_packet_bytes_length,
			server_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_client_socket_factory)
		_client_sockets = []
		_client_sockets_threads = []
		_client_sockets_semaphore = Semaphore()

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
		_server_socket.stop_accepting_clients()

	def test_client_messages_0(self):
		# send basic text message from one client to the server

		_to_client_packet_bytes_length = 4
		_to_server_packet_bytes_length = 4

		_server_sockets = []  # type: List[ClientSocket]
		_server_sockets_semaphore = Semaphore()

		def _on_accepted_client_method(client_socket: ClientSocket):
			print(f"Connected to client: {client_socket}")
			_server_sockets_semaphore.acquire()
			_server_sockets.append(client_socket)
			_server_sockets_semaphore.release()

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_client_packet_bytes_length=_to_client_packet_bytes_length,
			listening_limit_total=1,
			accept_timeout_seconds=0.2,
			client_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_clients(
			on_accepted_client_method=_on_accepted_client_method
		)
		time.sleep(1)
		_client_socket_factory = ClientSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_server_packet_bytes_length=_to_server_packet_bytes_length,
			server_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_client_socket_factory)
		_client_socket = _client_socket_factory.get_client_socket()
		self.assertIsNotNone(_client_socket)
		_expected_line = "test"
		_client_socket.write(_expected_line)
		_client_socket.close()
		_server_socket.stop_accepting_clients()

		self.assertEqual(1, len(_server_sockets))
		_actual_line = _server_sockets[0].read()
		self.assertEqual(_expected_line, _actual_line)
		_server_sockets[0].close()
		_server_socket.close()

	def test_client_messages_1(self):
		# send multiple text messages from one client to the server

		_to_client_packet_bytes_length = 4
		_to_server_packet_bytes_length = 4

		_server_sockets = []  # type: List[ClientSocket]
		_server_sockets_semaphore = Semaphore()

		def _on_accepted_client_method(client_socket: ClientSocket):
			print(f"Connected to client: {client_socket}")
			_server_sockets_semaphore.acquire()
			_server_sockets.append(client_socket)
			_server_sockets_semaphore.release()

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_client_packet_bytes_length=_to_client_packet_bytes_length,
			listening_limit_total=1,
			accept_timeout_seconds=0.2,
			client_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_clients(
			on_accepted_client_method=_on_accepted_client_method
		)
		time.sleep(1)
		_client_socket_factory = ClientSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_server_packet_bytes_length=_to_server_packet_bytes_length,
			server_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_client_socket_factory)
		_client_socket = _client_socket_factory.get_client_socket()
		self.assertIsNotNone(_client_socket)
		_expected_lines = ["test", "right", "here"]
		for _expected_line in _expected_lines:
			_client_socket.write(_expected_line)
		print(f"closing _client_socket")
		_client_socket.close()
		print(f"closed _client_socket")
		_server_socket.stop_accepting_clients()

		self.assertEqual(1, len(_server_sockets))
		for _expected_line in _expected_lines:
			_actual_line = _server_sockets[0].read()
			self.assertEqual(_expected_line, _actual_line)

		_server_sockets[0].close()
		_server_socket.close()

	def test_client_messages_2(self):
		# send multiple text messages with unusual characters from one client to the server

		_to_client_packet_bytes_length = 1024 * 3
		_to_server_packet_bytes_length = 1024 * 4
		_server_sockets = []  # type: List[ClientSocket]
		_server_sockets_semaphore = Semaphore()

		def _on_accepted_client_method(client_socket: ClientSocket):
			#print(f"Connected to client: {client_socket}")
			_server_sockets_semaphore.acquire()
			_server_sockets.append(client_socket)
			_server_sockets_semaphore.release()

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_client_packet_bytes_length=_to_client_packet_bytes_length,
			listening_limit_total=1,
			accept_timeout_seconds=0.2,
			client_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_clients(
			on_accepted_client_method=_on_accepted_client_method
		)
		time.sleep(1)
		_client_socket_factory = ClientSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_server_packet_bytes_length=_to_server_packet_bytes_length,
			server_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_client_socket_factory)
		_client_socket = _client_socket_factory.get_client_socket()
		self.assertIsNotNone(_client_socket)
		_server_socket.stop_accepting_clients()

		_expected_lines = ["test", "", "1234567890" * 10**7]
		for _expected_line_index, _expected_line in enumerate(_expected_lines):
			_client_socket.write_async(_expected_line)

		self.assertEqual(1, len(_server_sockets))
		_actual_lines = []

		def _read_callback(text: str):
			_actual_lines.append(text)  # TODO is list.append thread-safe?
		for _expected_line_index in range(len(_expected_lines)):
			_server_sockets[0].read_async(_read_callback)

		print("waiting...")
		time.sleep(1.0)
		while _client_socket.is_writing() or _server_sockets[0].is_reading():
			print(f"_is_writing: {_client_socket.is_writing()} | _is_reading: {_server_sockets[0].is_reading()}")
			time.sleep(0.1)

		print("finished")

		self.assertEqual(3, len(_expected_lines))
		self.assertEqual(3, len(_actual_lines))

		#for _expected_line, _actual_line in zip(_expected_lines, _actual_lines):
		#	print(f"len(_expected_line): {len(_expected_line)}")
		#	print(f"len(_actual_line): {len(_actual_line)}")

		for _expected_line, _actual_line in zip(_expected_lines, _actual_lines):
			self.assertEqual(_expected_line, _actual_line)

		_client_socket.close()
		_server_sockets[0].close()
		_server_socket.close()

	def test_client_messages_3(self):
		# send massive amount of messages from one client to the server

		_to_client_packet_bytes_length = 1024 * 3
		_to_server_packet_bytes_length = 1024 * 4
		_server_sockets = []  # type: List[ClientSocket]
		_server_sockets_semaphore = Semaphore()

		def _on_accepted_client_method(client_socket: ClientSocket):
			#print(f"Connected to client: {client_socket}")
			_server_sockets_semaphore.acquire()
			_server_sockets.append(client_socket)
			_server_sockets_semaphore.release()

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_client_packet_bytes_length=_to_client_packet_bytes_length,
			listening_limit_total=1,
			accept_timeout_seconds=0.2,
			client_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_server_socket_factory)
		_server_socket = _server_socket_factory.get_server_socket()
		self.assertIsNotNone(_server_socket)
		_server_socket.start_accepting_clients(
			on_accepted_client_method=_on_accepted_client_method
		)
		time.sleep(1)
		_client_socket_factory = ClientSocketFactory(
			ip_address="0.0.0.0",
			port=_port,
			to_server_packet_bytes_length=_to_server_packet_bytes_length,
			server_read_failed_delay_seconds=0.1
		)
		self.assertIsNotNone(_client_socket_factory)
		_client_socket = _client_socket_factory.get_client_socket()
		self.assertIsNotNone(_client_socket)
		_server_socket.stop_accepting_clients()

		_expected_lines = []
		_messages_total = 100000
		for _index in range(_messages_total):
			_expected_lines.append(str(_index))
		for _expected_line_index, _expected_line in enumerate(_expected_lines):
			_client_socket.write_async(_expected_line)

		self.assertEqual(1, len(_server_sockets))
		_actual_lines = []

		def _read_callback(text: str):
			_actual_lines.append(text)  # TODO is list.append thread-safe?
		for _expected_line_index in range(len(_expected_lines)):
			_server_sockets[0].read_async(_read_callback)

		#print("waiting...")
		time.sleep(1.0)
		while _client_socket.is_writing() or _server_sockets[0].is_reading():
			#print(f"_is_writing: {_client_socket.is_writing()} | _is_reading: {_server_sockets[0].is_reading()}")
			time.sleep(0.1)

		#print("finished")

		self.assertEqual(_messages_total, len(_expected_lines))
		self.assertEqual(_messages_total, len(_actual_lines))

		#for _expected_line, _actual_line in zip(_expected_lines, _actual_lines):
		#	print(f"len(_expected_line): {len(_expected_line)}")
		#	print(f"len(_actual_line): {len(_actual_line)}")

		for _expected_line, _actual_line in zip(_expected_lines, _actual_lines):
			self.assertEqual(_expected_line, _actual_line)

		_client_socket.close()
		_server_sockets[0].close()
		_server_socket.close()

	def test_get_machine_guid_0(self):
		# try to get the same guid from this machine
		_first_guid = get_machine_guid()
		_second_guid = get_machine_guid()
		self.assertEqual(_first_guid, _second_guid)
