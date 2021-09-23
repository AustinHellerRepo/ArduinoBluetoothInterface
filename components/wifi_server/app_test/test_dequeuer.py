import unittest
from app.dequeuer import Dequeuer, ClientSocketFactory, DatabaseFactory
from austin_heller_repo.socket import ServerSocketFactory, ClientSocket
import json
import time


class MainTest(unittest.TestCase):

	def test_initialize_0(self):
		# initialize dequeuer

		_database_factory = DatabaseFactory()
		_client_socket_factory = ClientSocketFactory(
			to_server_packet_bytes_length=4096,
			server_read_failed_delay_seconds=0.1
		)

		_dequeuer = Dequeuer(
			database_factory=_database_factory,
			client_socket_factory=_client_socket_factory,
			polling_thread_delay_seconds=1.0
		)

	def test_enqueue_and_dequeue_0(self):
		# enqueue message and then dequeue message but ensure transmission was not dequeued yet
		_database_factory = DatabaseFactory()
		_client_socket_factory = ClientSocketFactory(
			to_server_packet_bytes_length=4096,
			server_read_failed_delay_seconds=0.1
		)

		_dequeuer = Dequeuer(
			database_factory=_database_factory,
			client_socket_factory=_client_socket_factory,
			polling_thread_delay_seconds=1.0
		)

		# enqueue transmission

		_source_port = 25743
		_destination_port = 28932

		_database = _database_factory.get_database()

		_client = _database.insert_client(
			ip_address="127.0.0.1"
		)

		_source_device = _database.insert_device(
			device_guid="42A070EE-206D-49B8-9EEB-B54368807787",
			client_guid=_client.get_client_guid(),
			purpose_guid="B1901B73-8EC2-4AAC-825C-528FEC605BC6",
			socket_port=_source_port
		)

		_destination_device = _database.insert_device(
			device_guid="B4083458-D8DE-4387-9985-726E2A4EFDD5",
			client_guid=_client.get_client_guid(),
			purpose_guid="39A5E131-A7D7-41B7-B802-E9D45CD0B6F3",
			socket_port=_destination_port
		)

		_queue = _database.insert_queue(
			queue_guid="5F8E7D6C-107D-417D-99C1-E86EC88585FF"
		)

		_database.insert_transmission(
			queue_guid=_queue.get_queue_guid(),
			source_device_guid=_source_device.get_device_guid(),
			client_guid=_client.get_client_guid(),
			transmission_json_string=json.dumps({
				"test": True
			}),
			destination_device_guid=_destination_device.get_device_guid()
		)

		time.sleep(2.0)

		_transmission_dequeue = _database.get_next_transmission_dequeue(
			client_guid=_client.get_client_guid()
		)

		self.assertIsNotNone(_transmission_dequeue)

	def test_enqueue_and_dequeue_1(self):
		# enqueue message and then dequeue message
		_database_factory = DatabaseFactory()
		_client_socket_factory = ClientSocketFactory(
			to_server_packet_bytes_length=4096,
			server_read_failed_delay_seconds=0.1
		)

		_dequeuer = Dequeuer(
			database_factory=_database_factory,
			client_socket_factory=_client_socket_factory,
			polling_thread_delay_seconds=1.0
		)

		# enqueue transmission

		_source_port = 25743
		_destination_port = 28932

		_database = _database_factory.get_database()

		_client = _database.insert_client(
			ip_address="0.0.0.0"
		)

		_source_device = _database.insert_device(
			device_guid="42A070EE-206D-49B8-9EEB-B54368807787",
			client_guid=_client.get_client_guid(),
			purpose_guid="B1901B73-8EC2-4AAC-825C-528FEC605BC6",
			socket_port=_source_port
		)

		_destination_device = _database.insert_device(
			device_guid="B4083458-D8DE-4387-9985-726E2A4EFDD5",
			client_guid=_client.get_client_guid(),
			purpose_guid="39A5E131-A7D7-41B7-B802-E9D45CD0B6F3",
			socket_port=_destination_port
		)

		_queue = _database.insert_queue(
			queue_guid="5F8E7D6C-107D-417D-99C1-E86EC88585FF"
		)

		_expected_json_string = json.dumps({
			"test": True
		})

		_dequeuer_json_string = None
		_reporter_json_string = None

		_transmission = _database.insert_transmission(
			queue_guid=_queue.get_queue_guid(),
			source_device_guid=_source_device.get_device_guid(),
			client_guid=_client.get_client_guid(),
			transmission_json_string=_expected_json_string,
			destination_device_guid=_destination_device.get_device_guid()
		)
		self.assertIsNotNone(_transmission)
		print("test_dequeuer: inserted transmission")

		_server_socket_factory = ServerSocketFactory(
			to_client_packet_bytes_length=4096,
			listening_limit_total=10,
			accept_timeout_seconds=0.1,
			client_read_failed_delay_seconds=0.1
		)

		_source_server_socket = _server_socket_factory.get_server_socket()

		def _source_client_socket_connected(client_socket: ClientSocket):
			nonlocal _reporter_json_string
			_reporter_json_string = client_socket.read()
			client_socket.close()

		_source_server_socket.start_accepting_clients(
			host_ip_address="0.0.0.0",
			host_port=_source_port,
			on_accepted_client_method=_source_client_socket_connected
		)

		_destination_server_socket = _server_socket_factory.get_server_socket()

		def _destination_client_socket_connected(client_socket: ClientSocket):
			nonlocal _dequeuer_json_string
			_dequeuer_json_string = client_socket.read()
			client_socket.close()

		_destination_server_socket.start_accepting_clients(
			host_ip_address="0.0.0.0",
			host_port=_destination_port,
			on_accepted_client_method=_destination_client_socket_connected
		)

		_dequeuer.add_dequeuer()

		time.sleep(2.0)

		_dequeuer.remove_dequeuer()
		_dequeuer_errors = _dequeuer.get_errors()

		_destination_server_socket.stop_accepting_clients()
		_destination_server_socket.close()
		_source_server_socket.stop_accepting_clients()
		_source_server_socket.close()

		self.assertIsNotNone(_dequeuer_json_string)
		self.assertEqual(_expected_json_string, _dequeuer_json_string)
		self.assertIsNone(_reporter_json_string)
		self.assertEqual(0, len(_dequeuer_errors))
