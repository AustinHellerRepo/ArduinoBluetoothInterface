
class Module():

	def __init__(self):

		self.__send_method = None

	def set_send_method(self, *, send_method):
		self.__send_method = send_method

	def get_send_method(self):
		return self.__send_method

	def receive(self, *, data: str):
		raise NotImplementedError()

	def start(self):
		raise NotImplementedError()

	def stop(self):
		raise NotImplementedError()

	def get_purpose_guid(self) -> str:
		raise NotImplementedError()
