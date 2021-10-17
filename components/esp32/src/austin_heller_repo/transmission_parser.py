from austin_heller_repo.socket import ClientSocket, json, get_module_from_file_path, try_mkdir, join_path
from austin_heller_repo.module import ModuleReference


class ReceiveJsonTransmissionParser():

	def __init__(self, *, module_reference: ModuleReference):

		self.__module_reference = module_reference

	def process_transmission(self, *, header_json, client_socket: ClientSocket):

		_messages_total = header_json["meta"]["total"]
		for _message_index in range(_messages_total):
			_client_socket_message = client_socket.read()
			self.__module_reference.get().receive(
				data=_client_socket_message
			)


class ChangePurposeTransmissionParser():

	def __init__(self, *, module_reference: ModuleReference, git_clone_directory_path: str, device_guid: str, send_message_method, get_devices_by_purpose_method, on_ready_method):

		self.__module_reference = module_reference
		self.__git_clone_directory_path = git_clone_directory_path
		self.__device_guid = device_guid
		self.__send_message_method = send_message_method
		self.__get_devices_by_purpose_method = get_devices_by_purpose_method
		self.__on_ready_method = on_ready_method

	def process_transmission(self, *, header_json, client_socket: ClientSocket):

		self.__module_reference.get().stop()

		_module_name = header_json["meta"]["module_name"]
		_directory_paths = header_json["meta"]["directory_paths"]
		_files_total = header_json["meta"]["files_total"]

		for _directory_path in _directory_paths:
			try_mkdir(_directory_path)

		_messages_total = header_json["meta"]["total"]
		for _message_index in range(_messages_total):
			_file_meta_json_string = client_socket.read()
			_file_meta_json = json.loads(_file_meta_json_string)
			_file_path = _file_meta_json["file_path"]
			client_socket.download(_file_path)

		_module_file_path = join_path(self.__git_clone_directory_path, _module_name, "module.py")

		_module_class = get_module_from_file_path(_module_file_path, _module_name)
		_module = _module_class.ImplementedModule(
			device_guid=self.__device_guid,
			send_message_method=self.__send_message_method,
			get_devices_by_purpose_method=self.__get_devices_by_purpose_method,
			on_ready_method=self.__on_ready_method
		)

		# update the reference
		self.__module_reference.set(
			module=_module
		)

		self.__module_reference.get().start()  # this module will eventually call the on_ready method that will announce the device and supply it with its instance_guid
