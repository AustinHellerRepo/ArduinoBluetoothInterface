
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


class ReadWriteSocket():

	def __init__(self, *, socket: socket.socket, read_failed_delay_seconds: float):

		self.__socket = socket
		self.__read_failed_delay_seconds = read_failed_delay_seconds

		self.__readable_socket = None

		self.__initialize()

	def __initialize(self):

		if not hasattr(self.__socket, "readline"):
			self.__readable_socket = self.__socket.makefile("rwb")
		else:
			self.__readable_socket = self.__socket

	def read(self, bytes_length: int):

		_remaining_bytes_length = bytes_length
		_bytes_packets = []
		_read_bytes = None
		while _remaining_bytes_length != 0:
			_read_bytes = self.__readable_socket.read(_remaining_bytes_length)
			if _read_bytes is not None:
				_bytes_packets.append(_read_bytes)
				_remaining_bytes_length -= len(_read_bytes)
			else:
				if self.__read_failed_delay_seconds > 0:
					time.sleep(self.__read_failed_delay_seconds)
		_bytes = b"".join(_bytes_packets)
		return _bytes

	def write(self, data: bytes):

		self.__readable_socket.write(data)
		self.__readable_socket.flush()

	def close(self):

		if self.__readable_socket != self.__socket:
			self.__readable_socket.close()
		self.__socket.close()


class ClientSocket():

	def __init__(self, *, socket: socket.socket, packet_bytes_length: int, read_failed_delay_seconds: float):

		self.__socket = socket
		self.__packet_bytes_length = packet_bytes_length
		self.__read_failed_delay_seconds = read_failed_delay_seconds

		self.__read_write_socket = None  # type: ReadWriteSocket
		self.__is_writing = False
		self.__is_reading = False
		self.__write_semaphore = Semaphore()
		self.__read_semaphore = Semaphore()
		self.__writing_async_depth = 0
		self.__writing_async_depth_semaphore = Semaphore()
		self.__reading_async_depth = 0
		self.__reading_async_depth_semaphore = Semaphore()
		self.__writing_data_queue = []
		self.__writing_data_queue_semaphore = Semaphore()
		self.__reading_callback_queue = []
		self.__reading_callback_queue_semaphore = Semaphore()

		self.__initialize()

	def __initialize(self):

		self.__read_write_socket = ReadWriteSocket(
			socket=self.__socket,
			read_failed_delay_seconds=self.__read_failed_delay_seconds
		)

	def is_writing(self) -> bool:
		return self.__is_writing or self.__writing_async_depth > 0

	def is_reading(self) -> bool:
		return self.__is_reading or self.__reading_async_depth > 0

	def write_async(self, text: str, delay_between_packets_seconds: float = 0, index: int = 0):

		self.__writing_data_queue_semaphore.acquire()
		self.__writing_data_queue.append((text, delay_between_packets_seconds))
		self.__writing_data_queue_semaphore.release()

		_thread_started_semaphore = Semaphore()
		_thread_started_semaphore.acquire()

		def _write_thread_method():

			_thread_started_semaphore.release()  # release block in parent thread

			self.__write_semaphore.acquire()
			self.__is_writing = True

			self.__writing_data_queue_semaphore.acquire()
			_text, _delay_between_packets_seconds = self.__writing_data_queue.pop(0)
			self.__writing_data_queue_semaphore.release()

			self.write(
				text=_text,
				delay_between_packets_seconds=_delay_between_packets_seconds,
				acquire_semaphore=False
			)

			self.__writing_async_depth_semaphore.acquire()
			self.__writing_async_depth -= 1
			if self.__writing_async_depth == 0:
				self.__is_writing = False
			self.__writing_async_depth_semaphore.release()

			self.__write_semaphore.release()

		self.__writing_async_depth_semaphore.acquire()
		self.__writing_async_depth += 1  # in this moment, the socket "is writing" until all threads are done
		self.__writing_async_depth_semaphore.release()

		_write_thread = start_thread(
			target=_write_thread_method
		)

		_thread_started_semaphore.acquire()  # block here until release in thread method
		_thread_started_semaphore.release()

	def write(self, text: str, delay_between_packets_seconds: float = 0, acquire_semaphore: bool = True):

		if acquire_semaphore:
			self.__write_semaphore.acquire()
			self.__is_writing = True

		_text_bytes = text.encode()
		_text_bytes_length = len(_text_bytes)
		_packet_bytes_length = self.__packet_bytes_length
		_packets_total = int((_text_bytes_length + _packet_bytes_length - 1)/_packet_bytes_length)
		_packets_total_bytes = _packets_total.to_bytes(8, "big")

		self.__read_write_socket.write(_packets_total_bytes)

		for _packet_index in range(_packets_total):
			_current_packet_bytes_length = min(_text_bytes_length - _packet_bytes_length * _packet_index, _packet_bytes_length)
			_current_packet_bytes_length_bytes = _current_packet_bytes_length.to_bytes(8, "big")  # TODO fix based on possible maximum

			self.__read_write_socket.write(_current_packet_bytes_length_bytes)

			_current_text_bytes_index = _packet_index * _packet_bytes_length
			_packet_bytes = _text_bytes[_current_text_bytes_index:_current_text_bytes_index + _current_packet_bytes_length]

			self.__read_write_socket.write(_packet_bytes)

			if delay_between_packets_seconds > 0:
				time.sleep(delay_between_packets_seconds)

		if acquire_semaphore:
			self.__writing_async_depth_semaphore.acquire()
			if self.__writing_async_depth == 0:
				self.__is_writing = False
			self.__writing_async_depth_semaphore.release()
			self.__write_semaphore.release()

	def read_async(self, callback, delay_between_packets_seconds: float = 0, index: int = 0):

		self.__reading_callback_queue_semaphore.acquire()
		self.__reading_callback_queue.append((callback, delay_between_packets_seconds))
		self.__reading_callback_queue_semaphore.release()

		_thread_started_semaphore = Semaphore()
		_thread_started_semaphore.acquire()

		def _read_thread_method():

			_thread_started_semaphore.release()  # release block in parent thread

			self.__read_semaphore.acquire()
			self.__is_reading = True

			self.__reading_callback_queue_semaphore.acquire()
			_callback, _delay_between_packets_seconds = self.__reading_callback_queue.pop(0)
			self.__reading_callback_queue_semaphore.release()

			_text = self.read(
				delay_between_packets_seconds=_delay_between_packets_seconds,
				acquire_semaphore=False
			)
			_callback(_text)

			self.__reading_async_depth_semaphore.acquire()
			self.__reading_async_depth -= 1
			if self.__reading_async_depth == 0:
				self.__is_reading = False
			self.__reading_async_depth_semaphore.release()

			self.__read_semaphore.release()

		self.__reading_async_depth_semaphore.acquire()
		self.__reading_async_depth += 1
		self.__reading_async_depth_semaphore.release()

		_read_thread = start_thread(
			target=_read_thread_method
		)

		_thread_started_semaphore.acquire()  # block here until release in thread method
		_thread_started_semaphore.release()

	def read(self, delay_between_packets_seconds: float = 0, acquire_semaphore: bool = True) -> str:

		if acquire_semaphore:
			self.__read_semaphore.acquire()
			self.__is_reading = True

		_packets_total_bytes = self.__read_write_socket.read(8)  # TODO only send the number of bytes required to transmit based on self.__packet_bytes_length
		_packets_total = int.from_bytes(_packets_total_bytes, "big")
		_packets = []
		if _packets_total != 0:
			for _packet_index in range(_packets_total):
				_text_bytes_length_string_bytes = self.__read_write_socket.read(8)
				_text_bytes_length = int.from_bytes(_text_bytes_length_string_bytes, "big")
				_text_bytes = self.__read_write_socket.read(_text_bytes_length)
				_packets.append(_text_bytes)
				if delay_between_packets_seconds > 0:
					time.sleep(delay_between_packets_seconds)
		_text_bytes = b"".join(_packets)

		if acquire_semaphore:
			self.__reading_async_depth_semaphore.acquire()
			if self.__reading_async_depth == 0:
				self.__is_reading = False
			self.__reading_async_depth_semaphore.release()
			self.__read_semaphore.release()

		return _text_bytes.decode()

	def close(self):

		self.__read_write_socket.close()


class ClientSocketFactory():

	def __init__(self, *, ip_address: str, port: int, to_server_packet_bytes_length: int, server_read_failed_delay_seconds: float):

		self.__ip_address = ip_address
		self.__port = port
		self.__to_server_packet_bytes_length = to_server_packet_bytes_length
		self.__server_read_failed_delay_seconds = server_read_failed_delay_seconds

	def get_client_socket(self) -> ClientSocket:
		_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		_socket.connect((self.__ip_address, self.__port))
		return ClientSocket(
			socket=_socket,
			packet_bytes_length=self.__to_server_packet_bytes_length,
			read_failed_delay_seconds=self.__server_read_failed_delay_seconds
		)


class ServerSocket():

	def __init__(self, *, ip_address: str, port: int, to_client_packet_bytes_length: int, listening_limit_total: int, accept_timeout_seconds: float, client_read_failed_delay_seconds: float):

		self.__ip_address = ip_address
		self.__port = port
		self.__to_client_packet_bytes_length = to_client_packet_bytes_length
		self.__listening_limit_total = listening_limit_total
		self.__accept_timeout_seconds = accept_timeout_seconds
		self.__client_read_failed_delay_seconds = client_read_failed_delay_seconds

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

			def _process_connection_thread_method(connection_socket, address, to_client_packet_bytes_length, on_accepted_client_method, client_read_failed_delay_seconds: float):

				_accepted_socket = ClientSocket(
					socket=connection_socket,
					packet_bytes_length=to_client_packet_bytes_length,
					read_failed_delay_seconds=client_read_failed_delay_seconds
				)
				on_accepted_client_method(_accepted_socket)

			def _accepting_thread_method(to_client_packet_bytes_length, on_accepted_client_method, listening_limit_total, accept_timeout_seconds, client_read_failed_delay_seconds):
				self.__accepting_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.__accepting_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				self.__accepting_socket.bind(self.__bindable_address)
				self.__accepting_socket.listen(listening_limit_total)
				self.__accepting_socket.settimeout(accept_timeout_seconds)
				while self.__is_accepting:
					try:
						_connection_socket, _address = self.__accepting_socket.accept()
						_connection_socket.setblocking(False)
						_connection_thread = start_thread(_process_connection_thread_method, _connection_socket, _address, to_client_packet_bytes_length, on_accepted_client_method, client_read_failed_delay_seconds)
					except Exception as ex:
						if str(ex) == "[Errno 116] ETIMEDOUT":
							pass
						elif hasattr(socket, "timeout") and isinstance(ex, socket.timeout):
							pass
						else:
							print("ex: " + str(ex))
					if _is_threading_async:
						time.sleep(0.01)

			self.__accepting_thread = start_thread(_accepting_thread_method, self.__to_client_packet_bytes_length, on_accepted_client_method, self.__listening_limit_total, self.__accept_timeout_seconds, self.__client_read_failed_delay_seconds)

	def stop_accepting_clients(self):

		if not self.__is_accepting:
			raise Exception("Cannot stop accepting clients without first starting.")
		else:
			self.__is_accepting = False
			if self.__accepting_thread is not None:
				self.__accepting_thread.join()

	def close(self):

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
				 accept_timeout_seconds: float,
				 client_read_failed_delay_seconds: float):

		self.__ip_address = ip_address
		self.__port = port
		self.__to_client_packet_bytes_length = to_client_packet_bytes_length
		self.__listening_limit_total = listening_limit_total
		self.__accept_timeout_seconds = accept_timeout_seconds
		self.__client_read_failed_delay_seconds = client_read_failed_delay_seconds

	def get_server_socket(self) -> ServerSocket:

		return ServerSocket(
			ip_address=self.__ip_address,
			port=self.__port,
			to_client_packet_bytes_length=self.__to_client_packet_bytes_length,
			listening_limit_total=self.__listening_limit_total,
			accept_timeout_seconds=self.__accept_timeout_seconds,
			client_read_failed_delay_seconds=self.__client_read_failed_delay_seconds
		)
