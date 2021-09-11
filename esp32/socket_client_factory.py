
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
except ImportError:
	try:
		import _thread as threading
		def start_thread(target, *args, **kwargs):
			def _thread_method():
				target(*args, **kwargs)
			_thread = threading.start_new_thread(_thread_method, ())
			return _thread
	except ImportError:
		def start_thread(target, *args, **kwargs):
			target(*args, **kwargs)
			return None
		_is_threading_async = False

try:
	import ujson as json
except ImportError:
	import json

import time


class SocketClient():

	def __init__(self, *, ip_address: str, port: int):

		self.__ip_address = ip_address
		self.__port = port

		self.__bindable_address = None
		self.__is_accepting = False
		self.__accepting_thread = None  # type: threading.Thread

	def __initialize(self):

		self.__bindable_address = socket.getaddrinfo(self.__ip_address, self.__port, 0, socket.SOCK_STREAM)[0][-1]

	def start_accepting_messages(self, *, connections_total: int, processing_method):

		if self.__is_accepting:
			raise Exception(f"Cannot start accepting messages while already accepting.")
		else:

			def _process_connection_thread_method(connection_socket, address):
				if not hasattr(connection_socket, "readline"):
					_stream = connection_socket.makefile("rwb")
				else:
					_stream = connection_socket

				# request
				_line = _stream.readline().strip().decode()
				_method, _url, _raw_http_version = _line.split()
				_http_version = _raw_http_version.split("/", 1)[1]

				# headers
				_headers = {}
				_content_length = 0
				_line = None
				while _line != "":
					_line = _stream.readline().strip().decode()
					if _line != "":
						_header_name, _raw_header_value = _line.split(":", 1)
						_header_value = _raw_header_value.strip()
						_headers[_header_name] = _header_value
						if _header_name == "Content-Length":
							_content_length = int(_header_value)

				# body
				_body = b"" if _content_length == 0 else _stream.read(_content_length)

				print(f"Received data: \"{_body}\".")

				processing_method(_method, _url, _http_version, _headers, _body)

			def _accepting_thread_method():
				_accepting_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				_accepting_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				_accepting_socket.bind(self.__bindable_address)
				_accepting_socket.listen(connections_total)
				while self.__is_accepting:
					_connection_socket, _address = _accepting_socket.accept()
					_connection_socket.setblocking(False)
					_connection_thread = start_thread(_process_connection_thread_method, _connection_socket, _address)
					if _is_threading_async:
						time.sleep(0.01)

			self.__accepting_thread = start_thread(_accepting_thread_method)

	def stop_accepting_messages(self):

		if not self.__is_accepting:
			raise Exception(f"Cannot stop accepting messages without first starting.")
		else:
			self.__is_accepting = False
			if self.__accepting_thread is not None:
				self.__accepting_thread.join()


class SocketClientFactory():

	def __init__(self, *, ip_address: str, port: int):

		self.__ip_address = ip_address
		self.__port = port

	def get_socket_client(self) -> SocketClient:

		return SocketClient(
			ip_address=self.__ip_address,
			port=self.__port
		)
