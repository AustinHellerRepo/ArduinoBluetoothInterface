
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
		self.__writing_threads_running_total = 0
		self.__writing_threads_running_total_semaphore = Semaphore()
		self.__reading_threads_running_total = 0
		self.__reading_threads_running_total_semaphore = Semaphore()
		self.__writing_data_queue = []
		self.__writing_data_queue_semaphore = Semaphore()
		self.__is_writing_thread_running = False
		self.__write_started_semaphore = Semaphore()
		self.__reading_callback_queue = []
		self.__reading_callback_queue_semaphore = Semaphore()
		self.__is_reading_thread_running = False
		self.__read_started_semaphore = Semaphore()

		self.__initialize()

	def __initialize(self):

		self.__read_write_socket = ReadWriteSocket(
			socket=self.__socket,
			read_failed_delay_seconds=self.__read_failed_delay_seconds
		)

	def is_writing(self) -> bool:
		return self.__writing_threads_running_total > 0

	def is_reading(self) -> bool:
		return self.__reading_threads_running_total > 0

	def __write(self, *, delay_between_packets_seconds: float, text, is_async: bool):

		_blocking_semaphore = None
		self.__writing_data_queue_semaphore.acquire()
		if not is_async:
			_blocking_semaphore = Semaphore()
			_blocking_semaphore.acquire()
		self.__writing_data_queue.append((delay_between_packets_seconds, text, _blocking_semaphore))
		_is_writing_thread_needed = not self.__is_writing_thread_running
		if _is_writing_thread_needed:
			self.__is_writing_thread_running = True
		self.__writing_data_queue_semaphore.release()

		def _writing_thread_method():

			_is_running = True
			while _is_running:

				self.__writing_data_queue_semaphore.acquire()
				if len(self.__writing_data_queue) == 0:
					self.__is_writing_thread_running = False
					_is_running = False
					self.__writing_data_queue_semaphore.release()
					self.__writing_threads_running_total_semaphore.acquire()
					self.__writing_threads_running_total -= 1
					self.__writing_threads_running_total_semaphore.release()
				else:
					_delay_between_packets_seconds, _text, _blocking_semaphore = self.__writing_data_queue.pop(0)
					self.__writing_data_queue_semaphore.release()

					_text_bytes = _text.encode()
					_text_bytes_length = len(_text_bytes)
					_packet_bytes_length = self.__packet_bytes_length
					_packets_total = int((_text_bytes_length + _packet_bytes_length - 1) / _packet_bytes_length)
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

					if _blocking_semaphore is not None:
						_blocking_semaphore.release()

				time.sleep(0)  # permit other threads to take action

		if _is_writing_thread_needed:
			self.__writing_threads_running_total_semaphore.acquire()
			self.__writing_threads_running_total += 1
			self.__writing_threads_running_total_semaphore.release()
			_writing_thread = start_thread(_writing_thread_method)

		if not is_async:
			_blocking_semaphore.acquire()
			_blocking_semaphore.release()

	def write_async(self, text, delay_between_packets_seconds: float = 0):

		self.__write(
			delay_between_packets_seconds=delay_between_packets_seconds,
			text=text,
			is_async=True
		)

	def write(self, text: str, delay_between_packets_seconds: float = 0):

		self.__write(
			delay_between_packets_seconds=delay_between_packets_seconds,
			text=text,
			is_async=False
		)

	def __read(self, *, delay_between_packets_seconds: float, callback, is_async: bool):

		_blocking_semaphore = None
		self.__reading_callback_queue_semaphore.acquire()
		if not is_async:
			_blocking_semaphore = Semaphore()
			_blocking_semaphore.acquire()
		self.__reading_callback_queue.append((delay_between_packets_seconds, callback, _blocking_semaphore))
		_is_reading_thread_needed = not self.__is_reading_thread_running
		if _is_reading_thread_needed:
			self.__is_reading_thread_running = True
		self.__reading_callback_queue_semaphore.release()

		def _reading_thread_method():

			_is_running = True
			while _is_running:

				self.__reading_callback_queue_semaphore.acquire()
				if len(self.__reading_callback_queue) == 0:
					self.__is_reading_thread_running = False
					_is_running = False
					self.__reading_callback_queue_semaphore.release()
					self.__reading_threads_running_total_semaphore.acquire()
					self.__reading_threads_running_total -= 1
					self.__reading_threads_running_total_semaphore.release()
				else:
					_delay_between_packets_seconds, _callback, _blocking_semaphore = self.__reading_callback_queue.pop(0)
					self.__reading_callback_queue_semaphore.release()

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
					_text = _text_bytes.decode()

					_callback(_text)

					if _blocking_semaphore is not None:
						_blocking_semaphore.release()

				time.sleep(0)  # permit other threads to take action

		if _is_reading_thread_needed:
			self.__reading_threads_running_total_semaphore.acquire()
			self.__reading_threads_running_total += 1
			self.__reading_threads_running_total_semaphore.release()
			_reading_thread = start_thread(_reading_thread_method)

		if not is_async:
			_blocking_semaphore.acquire()
			_blocking_semaphore.release()

	def read_async(self, callback, delay_between_packets_seconds: float = 0):

		self.__read(
			delay_between_packets_seconds=delay_between_packets_seconds,
			callback=callback,
			is_async=True
		)

	def read(self, delay_between_packets_seconds: float = 0) -> str:

		_text = None
		_is_callback_successful = False

		def _callback(text: str):
			nonlocal _text
			nonlocal _is_callback_successful
			_text = text
			_is_callback_successful = True

		self.__read(
			delay_between_packets_seconds=delay_between_packets_seconds,
			callback=_callback,
			is_async=False
		)

		if not _is_callback_successful:
			raise Exception(f"Read process failed to block sync method before returning.")

		return _text

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
							self.__is_accepting = False
					if _is_threading_async:
						time.sleep(0.01)

			self.__accepting_thread = start_thread(_accepting_thread_method, self.__to_client_packet_bytes_length, on_accepted_client_method, self.__listening_limit_total, self.__accept_timeout_seconds, self.__client_read_failed_delay_seconds)

	def is_accepting_clients(self) -> bool:
		return self.__is_accepting

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
