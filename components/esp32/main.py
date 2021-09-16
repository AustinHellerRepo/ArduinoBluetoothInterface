from esp32_processor_factory import ServerSocketFactory, Esp32ProcessorFactory, Esp32Processor, time


_ip_address = "0.0.0.0"
_port = 24776
_connections_total = 3
_to_dequeuer_or_reporter_packet_bytes_length = 1024
_listening_limit_total = 10
_accept_timeout_seconds = 1.0
_client_read_failed_delay_seconds = 0.1
_wifi_settings_file_path = "/wifi_settings.json"

_server_socket_factory = ServerSocketFactory(
	ip_address=_ip_address,
	port=_port,
	to_client_packet_bytes_length=_to_dequeuer_or_reporter_packet_bytes_length,
	listening_limit_total=_listening_limit_total,
	accept_timeout_seconds=_accept_timeout_seconds,
	client_read_failed_delay_seconds=_client_read_failed_delay_seconds
)

_processor_factory = Esp32ProcessorFactory(
	server_socket_factory=_server_socket_factory,
	accepting_connections_total=_connections_total
)

_processor = _processor_factory.get_esp32_processor()
_processor.start()
