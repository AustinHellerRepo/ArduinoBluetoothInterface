from esp32_processor_factory import ServerSocketFactory, Esp32ProcessorFactory, Esp32Processor


_ip_address = "0.0.0.0"
_port = 24776
_connections_total = 3

#processing_method(_method, _url, _http_version, _headers, _body)


def _process_method(method: str, url: str, http_version: str, headers: Dict, body):
	print(f"Processing: {method} | {url} | {http_version} | {headers} | {body}")


_server_socket_factory = ServerSocketFactory(
	ip_address=_ip_address,
	port=_port,
	packet_bytes_length=_packet_bytes_length,
	listening_limit_total=_listening_limit_total,
	accept_timeout_seconds=_accept_timeout_seconds
)

_processor_factory = Esp32ProcessorFactory(
	socket_client_factory=_socket_client_factory,
	accepting_connections_total=_connections_total,
	processing_method=_process_method
)

_processor = _processor_factory.get_esp32_processor()
_processor.start()
