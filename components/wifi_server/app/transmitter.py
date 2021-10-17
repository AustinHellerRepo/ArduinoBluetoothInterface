from __future__ import annotations
from austin_heller_repo.socket import ThreadCycle, CyclingUnitOfWork, ThreadCycleCache, PreparedSemaphoreRequest, ClientSocketFactory, json
from app.database import DatabaseFactory, TransmissionDequeue
from app.transmission_parser import SendJsonTransmissionParser, ChangePurposeTransmissionParser, TransmissionParser
from typing import List


class TransmissionDequeueCyclingUnitOfWork(CyclingUnitOfWork):

	def __init__(self, *, database_factory: DatabaseFactory, client_socket_factory: ClientSocketFactory, send_json_transmission_parser_factory: SendJsonTransmissionParserFactory, change_purpose_transmission_parser_factory: ChangePurposeTransmissionParserFactory):
		super().__init__()

		self.__database_factory = database_factory
		self.__client_socket_factory = client_socket_factory
		self.__send_json_transmission_parser_factory = send_json_transmission_parser_factory
		self.__change_purpose_transmission_parser_factory = change_purpose_transmission_parser_factory

	def perform(self, *, try_get_next_work_queue_element_prepared_semaphore_request: PreparedSemaphoreRequest, acknowledge_nonempty_work_queue_prepared_semaphore_request: PreparedSemaphoreRequest) -> bool:

		print(f"TransmissionDequeueCyclingUnitOfWork: perform started")

		_database = self.__database_factory.get_database()
		_client = _database.insert_client(
			ip_address="0.0.0.0"
		)
		_transmission_dequeue = None  # type: TransmissionDequeue
		try_get_next_work_queue_element_prepared_semaphore_request.apply()
		_transmission_dequeue = _database.get_next_transmission_dequeue(
			client_guid=_client.get_client_guid()
		)
		if _transmission_dequeue is not None:
			acknowledge_nonempty_work_queue_prepared_semaphore_request.apply()
			_is_transmission_sent = False
			try:
				_parser_type = json.loads(_transmission_dequeue.get_transmission().get_stored_transmission_json_string())["parser_type"]

				_transmission_parser = None  # type: TransmissionParser
				if _parser_type == SendJsonTransmissionParser.get_type_name():
					_transmission_parser = self.__send_json_transmission_parser_factory.get_send_json_transmission_parser()
				elif _parser_type == ChangePurposeTransmissionParser.get_type_name():
					_transmission_parser = self.__change_purpose_transmission_parser_factory.get_change_purpose_transmission_parser()

				_client_socket = self.__client_socket_factory.get_client_socket()

				_client_socket.connect_to_server(
					ip_address=_transmission_dequeue.get_transmission().get_destination_device().get_last_known_client().get_ip_address(),
					port=_transmission_dequeue.get_transmission().get_destination_device().get_socket_port()
				)

				_transmission_parser.process_transmission(
					json_string=_transmission_dequeue.get_transmission().get_stored_transmission_json_string(),
					source_device_guid=_transmission_dequeue.get_transmission().get_source_device().get_device_guid(),
					source_instance_guid=_transmission_dequeue.get_transmission().get_source_device().get_instance_guid(),
					source_purpose_guid=_transmission_dequeue.get_transmission().get_source_device().get_purpose_guid(),
					destination_device_guid=_transmission_dequeue.get_transmission().get_destination_device().get_device_guid(),
					destination_instance_guid=_transmission_dequeue.get_transmission().get_destination_device().get_instance_guid(),
					destination_purpose_guid=_transmission_dequeue.get_transmission().get_destination_device().get_purpose_guid(),
					client_socket=_client_socket
				)

				_client_socket.close()
				_is_transmission_sent = True
			except Exception as ex:
				_database.transmission_failed(
					client_guid=_client.get_client_guid(),
					transmission_dequeue_guid=_transmission_dequeue.get_transmission_dequeue_guid(),
					error_message_json_string=str(ex)
				)

			if _is_transmission_sent:
				_database.transmission_completed(
					client_guid=_client.get_client_guid(),
					transmission_dequeue_guid=_transmission_dequeue.get_transmission_dequeue_guid()
				)

		print(f"TransmissionDequeueCyclingUnitOfWork: perform ended: {_transmission_dequeue}")

		return _transmission_dequeue is not None


class Transmitter():

	def __init__(self, *, transmission_dequeue_cycling_unit_of_work: TransmissionDequeueCyclingUnitOfWork, on_exception):

		self.__transmission_dequeue_cycling_unit_of_work = transmission_dequeue_cycling_unit_of_work
		self.__on_exception = on_exception

		self.__transmission_dequeue_thread_cycle_cache = None  # type: ThreadCycleCache

		self.__initialize()

	def __initialize(self):

		self.__transmission_dequeue_thread_cycle_cache = ThreadCycleCache(
			cycling_unit_of_work=self.__transmission_dequeue_cycling_unit_of_work,
			on_exception=self.__on_exception
		)

	def trigger_transmission_dequeue(self):

		self.__transmission_dequeue_thread_cycle_cache.try_add()

	def dispose(self):

		self.__transmission_dequeue_thread_cycle_cache.clear()
