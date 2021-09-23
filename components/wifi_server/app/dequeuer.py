from __future__ import annotations
from app.database import DatabaseFactory, TransmissionDequeue
from austin_heller_repo.socket import ClientSocketFactory, ThreadDelay, EncapsulatedThread, BooleanReference, Semaphore, StringReference
from typing import List, Tuple


class Dequeuer():

	def __init__(self, *, database_factory: DatabaseFactory, client_socket_factory: ClientSocketFactory, polling_thread_delay_seconds: float):

		self.__database_factory = database_factory
		self.__client_socket_factory = client_socket_factory
		self.__polling_thread_delay_seconds = polling_thread_delay_seconds

		self.__dequeue_encapsulated_threads = []  # type: List[EncapsulatedThread]
		self.__dequeue_encapsulated_threads_semaphore = Semaphore()
		self.__dequeue_errors = []  # type: List[str]
		self.__report_encapsulated_threads = []  # type: List[EncapsulatedThread]
		self.__report_encapsulated_threads_semaphore = Semaphore()
		self.__report_errors = []  # type: List[str]

	def add_dequeuer(self):

		self.__dequeue_encapsulated_threads_semaphore.acquire()

		_is_running_boolean_reference = BooleanReference(True)
		_polling_thread_delay = ThreadDelay()
		_error_string_reference = StringReference(None)

		def _dequeue_thread_method():
			try:
				_database = self.__database_factory.get_database()
				print(f"dequeuer: inserting client")
				_client = _database.insert_client(
					ip_address="0.0.0.0"
				)
				print(f"dequeuer: inserted client")
				while _is_running_boolean_reference.get():
					_transmission_dequeue = None  # type: TransmissionDequeue
					try:
						_transmission_dequeue = _database.get_next_transmission_dequeue(
							client_guid=_client.get_client_guid()
						)
						if _transmission_dequeue is not None:
							print("dequeuer: _transmission_dequeue is not None")
							_client_socket = self.__client_socket_factory.get_client_socket()
							_client_socket.connect_to_server(
								ip_address=_transmission_dequeue.get_transmission().get_destination_device().get_last_known_client().get_ip_address(),
								port=_transmission_dequeue.get_transmission().get_destination_device().get_socket_port()
							)
							_client_socket.write(
								text=_transmission_dequeue.get_transmission().get_transmission_json_string()
							)
							_client_socket.close()
							_database.transmission_completed(
								client_guid=_client.get_client_guid(),
								transmission_dequeue_guid=_transmission_dequeue.get_transmission_dequeue_guid()
							)
						else:
							print("dequeuer: _transmission_dequeue is None")
					except Exception as ex:
						print(f"dequeuer: {ex}")
						if _transmission_dequeue is None:
							_error_string_reference.set(str(ex))
						else:
							try:
								_database.transmission_failed(
									client_guid=_client.get_client_guid(),
									transmission_dequeue_guid=_transmission_dequeue.get_transmission_dequeue_guid(),
									error_message_json_string=str(ex)
								)
							except Exception as ex:
								print(f"dequeuer: {ex}")
								_error_string_reference.set(str(ex))
								_is_running_boolean_reference.set(False)
					if _is_running_boolean_reference.get():
						if _transmission_dequeue is None:
							_polling_thread_delay.try_sleep(
								seconds=self.__polling_thread_delay_seconds
							)
			except Exception as ex:
				print(f"dequeuer: {ex}")
				_error_string_reference.set(str(ex))
				_is_running_boolean_reference.set(False)

		_dequeuer_encapsulated_thread = EncapsulatedThread(
			target=_dequeue_thread_method,
			is_running_boolean_reference=_is_running_boolean_reference,
			polling_thread_delay=_polling_thread_delay,
			error_string_reference=_error_string_reference
		)
		_dequeuer_encapsulated_thread.start()
		self.__dequeue_encapsulated_threads.append(_dequeuer_encapsulated_thread)

		self.__dequeue_encapsulated_threads_semaphore.release()

	def remove_dequeuer(self):

		self.__dequeue_encapsulated_threads_semaphore.acquire()

		if len(self.__dequeue_encapsulated_threads) == 0:
			raise Exception("Failed to find any dequeue threads to remove.")

		_dequeue_encapsulated_thread = self.__dequeue_encapsulated_threads.pop(0)
		_dequeue_encapsulated_thread.stop()

		_last_error = _dequeue_encapsulated_thread.get_last_error()
		if _last_error is not None:
			self.__dequeue_errors.append(_last_error)

		self.__dequeue_encapsulated_threads_semaphore.release()

	def get_errors(self) -> List[str]:
		return self.__dequeue_errors.copy()

	def trigger_
