from esp32_processor_factory import SocketClientFactory, Esp32ProcessorFactory, Esp32Processor
from typing import Dict


_ip_address = "0.0.0.0"
_port = 24776
_connections_total = 3

#processing_method(_method, _url, _http_version, _headers, _body)


def _process_method(method: str, url: str, http_version: str, headers: Dict, body):
	print(f"Processing: {method} | {url} | {http_version} | {headers} | {body}")


_socket_client_factory = SocketClientFactory(
	ip_address=_ip_address,
	port=_port
)

_processor_factory = Esp32ProcessorFactory(
	socket_client_factory=_socket_client_factory,
	accepting_connections_total=_connections_total,
	processing_method=_process_method
)

_processor = _processor_factory.get_esp32_processor()
_processor.start()
