import sys
from app.dequeuer import Dequeuer
from austin_heller_repo.socket_client_factory import get_machine_guid, re, ServerSocketFactory, ClientSocket, json, time
from austin_heller_repo.api_interface import ApiInterfaceFactory


if len(sys.argv) != 11:
	_error = "Must provide comma-delimited list of queue guids, api base URL, listening port (0 if not listening), from server packet bytes length, to devices packet bytes length, server polling seconds as arguments to the script."
	print(_error)
	raise Exception(_error)
else:

	_queue_guids_comma_delimited = sys.argv[1]
	_api_base_url = sys.argv[2]
	_listening_port = int(sys.argv[3])
	_listening_limit_total = int(sys.argv[4])
	_accept_timeout_seconds = float(sys.argv[5])
	_device_read_failed_delay_seconds = float(sys.argv[6])
	_wifi_server_read_failed_delay_seconds = float(sys.argv[7])
	_to_devices_packet_bytes_length = int(sys.argv[8])
	_to_wifi_server_packet_bytes_length = int(sys.argv[9])
	_wifi_server_polling_seconds = float(sys.argv[10])

	_queue_guids = _queue_guids_comma_delimited.split(",")
	if len(_queue_guids) == 0:
		raise Exception(f"Failed to supply comma-delimited list of queue guids: \"{_queue_guids_comma_delimited}\".")

	_guid_regex = re.compile("^[0-9A-F]{8}\-[0-9A-F]{4}\-[0-9A-F]{4}\-[0-9A-F]{4}\-[0-9A-F]{12}$")
	for _queue_guid in _queue_guids:
		if _guid_regex.search(_queue_guid) is None:
			_error = f"Provided queue guid is not in the proper format: \"{_queue_guid}\"."
			print(_error)
			raise Exception(_error)

	_dequeuer_guid = get_machine_guid()

	_api_interface_factory = ApiInterfaceFactory(
		api_base_url=_api_base_url
	)

	_server_socket_factory = ServerSocketFactory(
		ip_address="0.0.0.0",
		port=_listening_port,
		to_client_packet_bytes_length=_to_wifi_server_packet_bytes_length,
		listening_limit_total=_listening_limit_total,
		accept_timeout_seconds=_accept_timeout_seconds,
		client_read_failed_delay_seconds=_device_read_failed_delay_seconds
	)

	_dequeuer = Dequeuer(
		dequeuer_guid=_dequeuer_guid,
		queue_guids=_queue_guids,
		api_interface_factory=_api_interface_factory,
		server_socket_factory=_server_socket_factory,
		wifi_server_polling_seconds=_wifi_server_polling_seconds,
		to_devices_packet_bytes_length=_to_devices_packet_bytes_length,
		to_wifi_server_packet_bytes_length=_to_wifi_server_packet_bytes_length,
		device_read_failed_delay_seconds=_wifi_server_read_failed_delay_seconds,
		is_informed_of_enqueue=(_listening_port != 0),
		listening_port=(None if _listening_port == 0 else _listening_port)
	)

	_dequeuer.start()

	while _dequeuer.is_running():
		time.sleep(1.0)

	_dequeuer.stop()
