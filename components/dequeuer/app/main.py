import sys
from app.dequeuer import Dequeuer
from austin_heller_repo.socket_client_factory import get_machine_guid, re, ServerSocketFactory, ClientSocket, json, time
from austin_heller_repo.api_interface import ApiInterfaceFactory


if len(sys.argv) != 3:
	_error = "Must provide queue guid, api base URL, listening port, from server packet bytes length, to devices packet bytes length, server polling seconds as arguments to the script."
	print(_error)
	raise Exception(_error)
else:

	_queue_guid = sys.argv[1]
	_api_base_url = sys.argv[2]
	_listening_port = int(sys.argv[3])
	_from_server_packet_bytes_length = int(sys.argv[4])
	_to_devices_packet_bytes_length = int(sys.argv[5])
	_server_polling_seconds = float(sys.argv[6])

	_guid_regex = re.compile("^[0-9A-F]{8}\-[0-9A-F]{4}\-[0-9A-F]{4}\-[0-9A-F]{4}\-[0-9A-F]{12}$")
	if _guid_regex.search(_queue_guid) is None:
		_error = f"Provided queue guid is not in the proper format: \"{_queue_guid}\"."
		print(_error)
		raise Exception(_error)
	else:

		_dequeuer_guid = get_machine_guid()

		_api_interface_factory = ApiInterfaceFactory(
			api_base_url=_api_base_url
		)

		_dequeuer = None  # type: Dequeuer

		def _on_accepted_client_method(client_socket: ClientSocket):
			_json_string = client_socket.read()
			_json = json.loads(_json_string)
			# TODO consider if anything should be expected from connected client, maybe some way to verify that it's actually coming from the server
			_dequeuer.try_process_next_transmission_dequeue()
			client_socket.close()

		_server_socket_factory = ServerSocketFactory(
			ip_address="0.0.0.0",
			port=_listening_port,
			packet_bytes_length=_from_server_packet_bytes_length,
			on_accepted_client_method=_on_accepted_client_method
		)

		_dequeuer = Dequeuer(
			dequeuer_guid=_dequeuer_guid,
			queue_guid=_queue_guid,
			api_interface_factory=_api_interface_factory,
			server_socket_factory=_server_socket_factory,
			server_polling_seconds=_server_polling_seconds,
			to_devices_packet_bytes_length=_to_devices_packet_bytes_length
		)

		_dequeuer.start()

		while _dequeuer.is_running():
			time.sleep(1.0)

		_dequeuer.stop()
