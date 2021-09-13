
try:
	import usocket as socket
except ImportError:
	import socket

_is_threading_async = True

try:
	import threading

	def start_thread(target, *args, **kwargs):
		_thread = threading.Thread(target=target, args=args, kwargs=kwargs)
		_thread.start()
		return _thread

	class Semaphore():

		def __init__(self):
			self.__lock = threading.Semaphore()

		def acquire(self):
			self.__lock.acquire()

		def release(self):
			self.__lock.release()

except ImportError:
	try:
		import _thread as threading

		def start_thread(target, *args, **kwargs):
			def _thread_method():
				target(*args, **kwargs)
			_thread = threading.start_new_thread(_thread_method, ())
			return _thread

		class Semaphore():

			def __init__(self):
				self.__lock = threading.allocate_lock()

			def acquire(self):
				self.__lock.acquire()

			def release(self):
				self.__lock.release()

	except ImportError:
		def start_thread(target, *args, **kwargs):
			target(*args, **kwargs)
			return None
		_is_threading_async = False

		class Semaphore():

			def __init__(self):
				self.__locks_total = 0

			def acquire(self):
				self.__locks_total += 1
				while self.__locks_total > 1:
					time.sleep(0.1)

			def release(self):
				self.__locks_total -= 1
				if self.__locks_total < 0:
					raise Exception("Unexpected number of releases.")

try:
	import ujson as json
except ImportError:
	import json

import hashlib

try:
	import network

	def get_machine_guid() -> str:
		_wlan = network.WLAN()
		_mac_bytes = _wlan.config("mac")
		_sha256 = hashlib.sha256()
		_sha256.update(_mac_bytes)
		_hashed_bytes = _sha256.digest()
		_hashed_hex_string = str(_hashed_bytes.hex())
		_guid = _hashed_hex_string[0:8] + "-" + _hashed_hex_string[8:12] + "-" + _hashed_hex_string[12:16] + "-" + _hashed_hex_string[16:20] + "-" + _hashed_hex_string[20:32]
		return _guid
except ImportError:
	import uuid

	def get_machine_guid() -> str:
		_node = uuid.getnode()
		_guid = str(uuid.UUID(int=_node, version=4))
		return _guid

import time
import re


class ClientSocket():

	def __init__(self, *, socket: socket.socket, packet_bytes_length: int):

		self.__socket = socket
		self.__packet_bytes_length = packet_bytes_length

		self.__readable_socket = None
		self.__is_writing = False
		self.__is_reading = False
		self.__write_semaphore = Semaphore()
		self.__read_semaphore = Semaphore()
		self.__writing_async_depth = 0
		self.__reading_async_depth = 0

		self.__initialize()

	def __initialize(self):

		if not hasattr(self.__socket, "readline"):
			self.__readable_socket = self.__socket.makefile("rwb")
		else:
			self.__readable_socket = self.__socket

	def is_writing(self) -> bool:
		return self.__is_writing or self.__writing_async_depth > 0

	def is_reading(self) -> bool:
		return self.__is_reading or self.__reading_async_depth > 0

	def write_async(self, text: str, delay_between_packets_seconds: float = 0):

		def _write_thread_method():

			self.__write_semaphore.acquire()
			self.__is_writing = True

			self.write(
				text=text,
				delay_between_packets_seconds=delay_between_packets_seconds,
				acquire_semaphore=False
			)
			self.__is_writing = False
			self.__writing_async_depth -= 1
			self.__write_semaphore.release()

		self.__writing_async_depth += 1  # in this moment, the socket "is writing" until all threads are done

		_write_thread = start_thread(
			target=_write_thread_method
		)

	_write_index = 0

	def write(self, text: str, delay_between_packets_seconds: float = 0, acquire_semaphore: bool = True):

		if acquire_semaphore:
			self.__write_semaphore.acquire()
			self.__is_writing = True

		_write_index = ClientSocket._write_index
		ClientSocket._write_index += 1

		_text_bytes = text.encode()
		_text_bytes_length = len(_text_bytes)
		#print(f"{_write_index}: _text_bytes_length: {_text_bytes_length}")
		_packet_bytes_length = self.__packet_bytes_length
		_packets_total = int((_text_bytes_length + _packet_bytes_length - 1)/_packet_bytes_length)
		_packets_total_bytes = _packets_total.to_bytes(8, "big")
		#print(f"{_write_index}: _packets_total_bytes: {_packets_total_bytes}")

		self.__readable_socket.write(_packets_total_bytes)
		self.__readable_socket.flush()

		for _packet_index in range(_packets_total):
			#print(f"{_write_index}: write: _packet_index: {_packet_index}/{_packets_total}")
			_current_packet_bytes_length = min(_text_bytes_length - _packet_bytes_length * _packet_index, _packet_bytes_length)
			_current_packet_bytes_length_bytes = _current_packet_bytes_length.to_bytes(8, "big")  # TODO fix based on possible maximum

			self.__readable_socket.write(_current_packet_bytes_length_bytes)
			self.__readable_socket.flush()

			_current_text_bytes_index = _packet_index * _packet_bytes_length
			_packet_bytes = _text_bytes[_current_text_bytes_index:_current_text_bytes_index + _current_packet_bytes_length]
			#print(f"{_write_index}: _packet_bytes: {_packet_bytes}")

			self.__readable_socket.write(_packet_bytes)
			self.__readable_socket.flush()

			if delay_between_packets_seconds > 0:
				time.sleep(delay_between_packets_seconds)

		if acquire_semaphore:
			self.__is_writing = False
			self.__write_semaphore.release()

	def read_async(self, callback, delay_between_packets_seconds: float = 0):

		def _read_thread_method():

			self.__read_semaphore.acquire()
			self.__is_reading = True

			_text = self.read(
				delay_between_packets_seconds=delay_between_packets_seconds,
				acquire_semaphore=False
			)
			callback(_text)

			self.__is_reading = False
			self.__reading_async_depth -= 1
			self.__read_semaphore.release()

		self.__reading_async_depth += 1

		_read_thread = start_thread(
			target=_read_thread_method
		)

	_read_index = 0

	def read(self, delay_between_packets_seconds: float = 0, acquire_semaphore: bool = True) -> str:

		if acquire_semaphore:
			self.__read_semaphore.acquire()
			self.__is_reading = True

		_read_index = ClientSocket._read_index
		ClientSocket._read_index += 1
		#print(f"{_read_index}: reading...")

		_packets_total_bytes = None
		while _packets_total_bytes is None:
			#print(f"{_read_index}: trying...")
			_packets_total_bytes = self.__readable_socket.read(8)  # TODO only send the number of bytes required to transmit based on self.__packet_bytes_length
			#print(f"{_read_index}: done: {_packets_total_bytes}")
			if _packets_total_bytes is None and delay_between_packets_seconds > 0:
				time.sleep(delay_between_packets_seconds)
		_packets_total = int.from_bytes(_packets_total_bytes, "big")
		#print(f"{_read_index}: _packets_total: {_packets_total}")
		_packets = []
		if _packets_total != 0:
			for _packet_index in range(_packets_total):
				_text_bytes_length_string_bytes = None
				while _text_bytes_length_string_bytes is None:
					_text_bytes_length_string_bytes = self.__readable_socket.read(8)
					if _text_bytes_length_string_bytes is None and delay_between_packets_seconds > 0:
						time.sleep(delay_between_packets_seconds)
				#print(f"{_read_index}: read: _text_bytes_length_string_bytes: {_text_bytes_length_string_bytes}")
				_text_bytes_length = int.from_bytes(_text_bytes_length_string_bytes, "big")
				_text_bytes = None
				while _text_bytes is None:
					_text_bytes = self.__readable_socket.read(_text_bytes_length)
					if _text_bytes is None and delay_between_packets_seconds > 0:
						time.sleep(delay_between_packets_seconds)
				#print(f"{_read_index}: _text_bytes: {_text_bytes}")
				_packets.append(_text_bytes)
				if delay_between_packets_seconds > 0:
					time.sleep(delay_between_packets_seconds)
		_text_bytes = b"".join(_packets)
		#print(f"{_read_index}: _text_bytes: {_text_bytes}")

		if acquire_semaphore:
			self.__is_reading = False
			self.__read_semaphore.release()

		return _text_bytes.decode()

	def close(self):

		#print(f"closing client socket...")
		if self.__readable_socket != self.__socket:
			self.__readable_socket.close()
		self.__socket.close()


class ClientSocketFactory():

	def __init__(self, *, ip_address: str, port: int, to_server_packet_bytes_length: int):

		self.__ip_address = ip_address
		self.__port = port
		self.__to_server_packet_bytes_length = to_server_packet_bytes_length

	def get_client_socket(self) -> ClientSocket:
		_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		_socket.connect((self.__ip_address, self.__port))
		return ClientSocket(
			socket=_socket,
			packet_bytes_length=self.__to_server_packet_bytes_length
		)


class ServerSocket():

	def __init__(self, *, ip_address: str, port: int, to_client_packet_bytes_length: int, listening_limit_total: int, accept_timeout_seconds: float):

		self.__ip_address = ip_address
		self.__port = port
		self.__to_client_packet_bytes_length = to_client_packet_bytes_length
		self.__listening_limit_total = listening_limit_total
		self.__accept_timeout_seconds = accept_timeout_seconds

		self.__bindable_address = None
		self.__is_accepting = False
		self.__accepting_thread = None  # type: threading.Thread
		self.__accepting_socket = None

		self.__initialize()

	def __initialize(self):

		self.__bindable_address = socket.getaddrinfo(self.__ip_address, self.__port, 0, socket.SOCK_STREAM)[0][-1]

	def start_accepting_clients(self, *, on_accepted_client_method):

		if self.__is_accepting:
			raise Exception("Cannot start accepting clients while already accepting.")
		else:

			self.__is_accepting = True

			def _process_connection_thread_method(connection_socket, address, to_client_packet_bytes_length, on_accepted_client_method):

				_accepted_socket = ClientSocket(
					socket=connection_socket,
					packet_bytes_length=to_client_packet_bytes_length
				)
				on_accepted_client_method(_accepted_socket)

			def _accepting_thread_method(to_client_packet_bytes_length, on_accepted_client_method, listening_limit_total, accept_timeout_seconds):
				self.__accepting_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.__accepting_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				self.__accepting_socket.bind(self.__bindable_address)
				self.__accepting_socket.listen(listening_limit_total)
				self.__accepting_socket.settimeout(accept_timeout_seconds)
				while self.__is_accepting:
					try:
						_connection_socket, _address = self.__accepting_socket.accept()
						_connection_socket.setblocking(False)
						_connection_thread = start_thread(_process_connection_thread_method, _connection_socket, _address, to_client_packet_bytes_length, on_accepted_client_method)
					except socket.timeout:
						pass
					except Exception as ex:
						print("ex: " + str(ex))
					if _is_threading_async:
						time.sleep(0.01)

			self.__accepting_thread = start_thread(_accepting_thread_method, self.__to_client_packet_bytes_length, on_accepted_client_method, self.__listening_limit_total, self.__accept_timeout_seconds)

	def stop_accepting_clients(self):

		if not self.__is_accepting:
			raise Exception("Cannot stop accepting clients without first starting.")
		else:
			self.__is_accepting = False
			if self.__accepting_thread is not None:
				self.__accepting_thread.join()

	def close(self):

		#print(f"closing server socket...")
		if self.__is_accepting:
			raise Exception("Cannot close without first stopping accepting clients.")
		else:
			self.__accepting_socket.close()


class ServerSocketFactory():

	def __init__(self, *,
				 ip_address: str,
				 port: int,
				 to_client_packet_bytes_length: int,
				 listening_limit_total: int,
				 accept_timeout_seconds: float):

		self.__ip_address = ip_address
		self.__port = port
		self.__to_client_packet_bytes_length = to_client_packet_bytes_length
		self.__listening_limit_total = listening_limit_total
		self.__accept_timeout_seconds = accept_timeout_seconds

	def get_server_socket(self) -> ServerSocket:

		return ServerSocket(
			ip_address=self.__ip_address,
			port=self.__port,
			to_client_packet_bytes_length=self.__to_client_packet_bytes_length,
			listening_limit_total=self.__listening_limit_total,
			accept_timeout_seconds=self.__accept_timeout_seconds
		)
