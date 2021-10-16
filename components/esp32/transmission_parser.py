from austin_heller_repo.socket import ClientSocket
from module import Module


class ReceiveJsonTransmissionParser():

	def __init__(self, *, module: Module):

		self.__module = module

	def process_transmission(self, *, header_json_string: str, client_socket: ClientSocket):


