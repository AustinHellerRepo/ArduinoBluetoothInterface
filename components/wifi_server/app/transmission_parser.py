from __future__ import annotations
from abc import ABC, abstractmethod
from austin_heller_repo.socket import Encryption, json, ClientSocket
import tempfile
import os
from app.git_interface import GitInterface


class TransmissionParser():

	def __init__(self):
		pass

	@staticmethod
	@abstractmethod
	def get_type_name() -> str:
		raise NotImplementedError()

	@abstractmethod
	def store_transmission(self, *, json_string: str) -> str:
		raise NotImplementedError()

	@abstractmethod
	def process_transmission(self, *, json_string: str, source_device_guid: str, source_instance_guid: str, source_purpose_guid: str, destination_device_guid: str, destination_instance_guid: str, destination_purpose_guid: str, client_socket: ClientSocket):
		raise NotImplementedError()


class EncryptedSendJsonTransmissionParser(TransmissionParser):

	def __init__(self, *, encryption: Encryption):
		super().__init__()

		self.__encryption = encryption

	@staticmethod
	def get_type_name():
		return "encrypted json"

	def store_transmission(self, *, json_string: str) -> str:
		_temp_file_path = tempfile.NamedTemporaryFile(delete=False)
		_encrypted_json_string_bytes = self.__encryption.encrypt(
			decrypted_data=json_string.encode()
		)
		with open(_temp_file_path.name, "wb") as _file_handle:
			_file_handle.write(_encrypted_json_string_bytes)

		_encapsulated_json_string = json.dumps({
			"parser_type": EncryptedSendJsonTransmissionParser.__name__,
			"file_path": _temp_file_path.name
		})
		return _encapsulated_json_string

	def process_transmission(self, *, json_string: str, source_device_guid: str, source_instance_guid: str, source_purpose_guid: str, destination_device_guid: str, destination_instance_guid: str, destination_purpose_guid: str, client_socket: ClientSocket):

		_json = json.loads(json_string)
		if "parser_type" not in _json:
			raise Exception(f"Provided json_string missing \"parser_type\" key. Found: \"{json_string}\".")
		elif _json["parser_type"] != EncryptedSendJsonTransmissionParser.__name__:
			raise Exception(f"Invalid parser. Found \"{_json['parser_type']}\".")
		elif "file_path" not in _json:
			raise Exception(f"Provided json_string missing \"file_path\" key. Found: \"{json_string}\".")
		elif not os.path.exists(_json["file_path"]):
			raise Exception(f"File missing: \"{_json['file_path']}\".")
		else:
			with open(_json["file_path"], "rb") as _file_handle:
				_encrypted_file_bytes = _file_handle.read()
			_decrypted_file_bytes = self.__encryption.decrypt(
				encrypted_data=_encrypted_file_bytes
			)
			_message = _decrypted_file_bytes.decode()
			client_socket.write(json.dumps({
				"type": "send message",
				"meta": {
					"total": 1
				},
				"routing": {
					"source_device_guid": source_device_guid,
					"source_instance_guid": source_instance_guid,
					"source_purpose_guid": source_purpose_guid,
					"destination_device_guid": destination_device_guid,
					"destination_instance_guid": destination_instance_guid,
					"destination_purpose_guid": destination_purpose_guid
				}
			}))
			client_socket.write(_message)
			os.unlink(_json["file_path"])


class SendJsonTransmissionParser(TransmissionParser):

	def __init__(self):
		super().__init__()

		pass

	@staticmethod
	def get_type_name() -> str:
		return "json"

	def store_transmission(self, *, json_string: str) -> str:
		_temp_file_path = tempfile.NamedTemporaryFile(delete=False)
		with open(_temp_file_path.name, "wb") as _file_handle:
			_file_handle.write(json_string.encode())

		_encapsulated_json_string = json.dumps({
			"parser_type": SendJsonTransmissionParser.__name__,
			"file_path": _temp_file_path.name
		})
		return _encapsulated_json_string

	def process_transmission(self, *, json_string: str, source_device_guid: str, source_instance_guid: str, source_purpose_guid: str, destination_device_guid: str, destination_instance_guid: str, destination_purpose_guid: str, client_socket: ClientSocket):

		_json = json.loads(json_string)
		if "parser_type" not in _json:
			raise Exception(f"Provided json_string missing \"parser_type\" key. Found: \"{json_string}\".")
		elif _json["parser_type"] != SendJsonTransmissionParser.__name__:
			raise Exception(f"Invalid parser. Found \"{_json['parser_type']}\".")
		elif "file_path" not in _json:
			raise Exception(f"Provided json_string missing \"file_path\" key. Found: \"{json_string}\".")
		elif not os.path.exists(_json["file_path"]):
			raise Exception(f"File missing: \"{_json['file_path']}\".")
		else:
			client_socket.write(json.dumps({
				"type": "send message",
				"meta": {
					"total": 1
				},
				"routing": {
					"source_device_guid": source_device_guid,
					"source_instance_guid": source_instance_guid,
					"source_purpose_guid": source_purpose_guid,
					"destination_device_guid": destination_device_guid,
					"destination_instance_guid": destination_instance_guid,
					"destination_purpose_guid": destination_purpose_guid
				}
			}))
			client_socket.upload(
				file_path=_json["file_path"]
			)
			os.unlink(_json["file_path"])


class SendJsonTransmissionParserFactory():

	def __init__(self):
		pass

	def get_send_json_transmission_parser(self) -> SendJsonTransmissionParser:
		return SendJsonTransmissionParser()


class ChangePurposeTransmissionParser(TransmissionParser):

	def __init__(self):
		super().__init__()

	@staticmethod
	def get_type_name() -> str:
		return "change purpose"

	def store_transmission(self, *, json_string: str) -> str:
		_temp_file_path = tempfile.NamedTemporaryFile(delete=False)
		with open(_temp_file_path.name, "wb") as _file_handle:
			_file_handle.write(json_string.encode())

		_encapsulated_json_string = json.dumps({
			"parser_type": ChangePurposeTransmissionParser.__name__,
			"file_path": _temp_file_path.name
		})
		return _encapsulated_json_string

	def process_transmission(self, *, json_string: str, source_device_guid: str, source_instance_guid: str, source_purpose_guid: str, destination_device_guid: str, destination_instance_guid: str, destination_purpose_guid: str, client_socket: ClientSocket):

		_json = json.loads(json_string)
		if "parser_type" not in _json:
			raise Exception(f"Provided json_string missing \"parser_type\" key. Found: \"{json_string}\".")
		elif _json["parser_type"] != ChangePurposeTransmissionParser.__name__:
			raise Exception(f"Invalid parser. Found \"{_json['parser_type']}\".")
		elif "file_path" not in _json:
			raise Exception(f"Provided json_string missing \"file_path\" key. Found: \"{json_string}\".")
		elif not os.path.exists(_json["file_path"]):
			raise Exception(f"File missing: \"{_json['file_path']}\".")
		else:
			_transmission_json = None
			with open(_json["file_path"], "rb") as _file_handle:
				_transmission_json = json.loads(_file_handle.read().decode())
			if "git_repository_url" not in _transmission_json:
				raise Exception(f"Transmission missing \"git_repository_url\". Found: \"{_transmission_json}\".")
			_temp_directory = tempfile.TemporaryDirectory()
			try:
				_git_repository_url = _transmission_json["git_repository_url"]
				GitInterface.clone(
					git_repository_url=_git_repository_url,
					git_clone_directory_path=_temp_directory.name,
					delay_clone_completed_polling_seconds=0.1
				)
				_to_send_directory_paths_and_parent_directory_paths = [
					(_temp_directory.name, "")
				]
				_to_make_directory_paths = []
				_to_upload_local_file_paths_and_destination_file_paths = []
				while len(_to_send_directory_paths_and_parent_directory_paths) != 0:
					_directory_path, _parent_directory_path = _to_send_directory_paths_and_parent_directory_paths.pop(0)
					for _file_name in os.listdir(_directory_path):
						_file_path = os.path.join(_directory_path, _file_name)
						if os.path.isdir(_file_path):
							_to_make_directory_path = os.path.join(_parent_directory_path, _file_name)
							_to_make_directory_paths.append(_to_make_directory_path)
							_to_send_directory_paths_and_parent_directory_paths.append((_file_path, _to_make_directory_path))
						else:
							_destination_file_path = os.path.join(_parent_directory_path, _file_name)
							_to_upload_local_file_paths_and_destination_file_paths.append((_file_path, _destination_file_path))
				client_socket.write(json.dumps({
					"type": "change purpose",
					"meta": {
						"module_name": _git_repository_url.split("/")[-1],
						"directory_paths": _to_make_directory_paths,
						"files_total": len(_to_upload_local_file_paths_and_destination_file_paths)
					},
					"routing": {
						"source_device_guid": source_device_guid,
						"source_instance_guid": source_instance_guid,
						"source_purpose_guid": source_purpose_guid,
						"destination_device_guid": destination_device_guid,
						"destination_instance_guid": destination_instance_guid,
						"destination_purpose_guid": destination_purpose_guid
					}
				}))
				for _local_file_path, _destination_file_path in _to_upload_local_file_paths_and_destination_file_paths:
					client_socket.write(json.dumps({
						"file_path": _destination_file_path
					}))
					client_socket.upload(
						file_path=_local_file_path
					)
			except Exception as ex:
				_temp_directory.cleanup()
				raise ex
			_temp_directory.cleanup()


class ChangePurposeTransmissionParserFactory():

	def __init__(self):
		pass

	def get_change_purpose_transmission_parser(self) -> ChangePurposeTransmissionParser:
		return ChangePurposeTransmissionParser()
