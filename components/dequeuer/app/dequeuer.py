from __future__ import annotations
from austin_heller_repo.api_interface import ApiInterfaceFactory, ApiInterface
from austin_heller_repo.socket_client_factory import ServerSocketFactory, start_thread, ClientSocketFactory, json, threading, Semaphore
from typing import List, Tuple, Dict, Callable
import time


class Dequeuer():

	def __init__(self, *, dequeuer_guid: str, queue_guid: str, api_interface_factory: ApiInterfaceFactory, server_socket_factory: ServerSocketFactory, server_polling_seconds: float, to_devices_packet_bytes_length: int):

		self.__dequeuer_guid = dequeuer_guid
		self.__queue_guid = queue_guid
		self.__api_interface_factory = api_interface_factory
		self.__server_socket_factory = server_socket_factory
		self.__server_polling_seconds = server_polling_seconds
		self.__to_devices_packet_bytes_length = to_devices_packet_bytes_length

		self.__process_thread = None  # type: threading.Thread
		self.__is_running_process_thread = False
		self.__process_transmission_dequeue_threads = []  # type: List[threading.Thread]
		self.__process_transmission_dequeue_threads_semaphore = Semaphore()

	def start(self):

		self.__is_running_process_thread = True

		if self.__process_thread is not None:
			raise Exception(f"Cannot start dequeuer without first stopping previous start.")
		else:

			def _process_thread_method(server_polling_seconds: float, try_announce_dequeuer: Callable[[], bool], try_process_next_transmission_dequeue: Callable[[], bool], join_completed_transmission_dequeue_threads: Callable[[], None], join_all_transmission_dequeue_threads: Callable[[], None]):
				_is_successful = try_announce_dequeuer()
				if _is_successful:
					_process_dequeue_index = 0
					while self.__is_running_process_thread:
						_is_successful = try_process_next_transmission_dequeue()
						if _is_successful:
							print(f"Processed transmission dequeue #{_process_dequeue_index}")
							_process_dequeue_index += 1
						time.sleep(server_polling_seconds)
						join_completed_transmission_dequeue_threads()
				self.__is_running_process_thread = False
				join_all_transmission_dequeue_threads()

			self.__process_thread = start_thread(_process_thread_method, self.__server_polling_seconds, self.try_announce_dequeuer, self.try_process_next_transmission_dequeue, self.join_completed_transmission_dequeue_threads, self.join_all_transmission_dequeue_threads)

	def try_announce_dequeuer(self) -> bool:
		_is_successful = False
		try:
			_api_interface = self.__api_interface_factory.get_api_interface()
			_api_interface.send_dequeuer_announcement(
				dequeuer_guid=self.__dequeuer_guid
			)
			_is_successful = True
		except Exception as ex:
			print(f"ex: {ex}")
		return _is_successful

	def try_process_next_transmission_dequeue(self) -> bool:
		_is_successful = False
		try:
			_api_interface = self.__api_interface_factory.get_api_interface()
			_transmission_dequeue = _api_interface.dequeue_next_transmission(
				dequeuer_guid=self.__dequeuer_guid,
				queue_guid=self.__queue_guid
			)
			if _transmission_dequeue is not None:

				def _process_transmission_dequeue_thread_method(transmission_dequeue: Dict, to_devices_packet_bytes_length: int, api_interface: ApiInterface):
					_transmission_dequeue_guid = None
					try:
						_transmission_dequeue_guid = transmission_dequeue["transmission_dequeue_guid"]
						_transmission = transmission_dequeue["transmission"]
						_destination_device = _transmission["destination_device"]
						_destination_client = _destination_device["last_known_client"]
						_ip_address = _destination_client["ip_address"]
						_port = _destination_device["socket_port"]
						_client_socket_factory = ClientSocketFactory(
							ip_address=_ip_address,
							port=_port,
							packet_bytes_length=to_devices_packet_bytes_length
						)
						_client_socket = _client_socket_factory.get_client_socket()
						_transmission_json_string = _transmission["transmission_json_string"]
						_client_socket.write(_transmission_json_string)
						_client_socket.close()
						api_interface.update_transmission_as_completed(
							transmission_dequeue_guid=_transmission_dequeue_guid
						)
					except Exception as ex:
						print(f"ex: {ex}")
						_error_message_json = {"exception": str(ex), "transmission_dequeue_guid": _transmission_dequeue_guid}
						if _transmission_dequeue_guid is None:
							print("Error: failed to send update of failure to api since _transmission_dequeue_guid is None.")
						else:
							api_interface.update_transmission_as_failed(
								transmission_dequeue_guid=_transmission_dequeue_guid,
								error_message_json=_error_message_json
							)

				_process_transmission_dequeue_thread = start_thread(_process_transmission_dequeue_thread_method, _transmission_dequeue, _api_interface)
				self.__process_transmission_dequeue_threads_semaphore.acquire()
				self.__process_transmission_dequeue_threads.append(_process_transmission_dequeue_thread)
				self.__process_transmission_dequeue_threads_semaphore.release()
			_is_successful = True
		except Exception as ex:
			print(f"ex: {ex}")
		return _is_successful

	def stop(self):

		if self.__process_thread is None:
			raise Exception(f"Cannot stop processing without first starting.")
		else:
			self.__is_running_process_thread = False
			self.__process_thread.join()

	def join_completed_transmission_dequeue_threads(self):

		_remove_indexes = []  # type: List[int]

		for _thread_index in range(len(self.__process_transmission_dequeue_threads)):
			if not self.__process_transmission_dequeue_threads[_thread_index].is_alive():
				_remove_indexes.append(_thread_index)

		self.__process_transmission_dequeue_threads_semaphore.acquire()
		for _thread_index in reversed(_remove_indexes):
			self.__process_transmission_dequeue_threads.pop(_thread_index)
		self.__process_transmission_dequeue_threads_semaphore.release()

	def join_all_transmission_dequeue_threads(self):

		self.__process_transmission_dequeue_threads_semaphore.acquire()
		for _thread in self.__process_transmission_dequeue_threads:
			_thread.join()
		self.__process_transmission_dequeue_threads.clear()
		self.__process_transmission_dequeue_threads_semaphore.release()
