import sys
import os

sys.path.append(os.getcwd())

import subprocess
import serial.tools.list_ports
import esptool
from typing import List
from io import StringIO
import re
import ampy.cli
from contextlib import redirect_stdout


class OutputCapture(list):
	def __enter__(self):
		self._stdout = sys.stdout
		sys.stdout = self._stringio = StringIO()
		return self

	def __exit__(self, *args):
		self.extend(self._stringio.getvalue().splitlines())
		del self._stringio  # free up some memory
		sys.stdout = self._stdout


_com_ports = serial.tools.list_ports.comports()

_device_names = []  # type: List[str]

for _com_port in _com_ports:
	_device_names.append(_com_port.device)

if len(_device_names) == 0:
	print("No devices found.")
else:
	_project_directory = input("Project directory: ")
	if _project_directory != "":
		_main_exists = False
		for _file_name in os.listdir(_project_directory):
			if _file_name == "main.py":
				_main_exists = True
				break
		if not _main_exists:
			_error = f"Failed to find main.py in project directory: \"{_project_directory}\"."
			print(_error)
			raise Exception(_error)

		print(f"Select COM port")
		for _device_name_index, _device_name in enumerate(_device_names):
			print(f"{_device_name_index}: {_device_name}")
		_user_input = input("Device index: ")
		if _user_input != "":
			_device_name_index = int(_user_input)
			_device_name = _device_names[_device_name_index]

			_baud_rates = [921600, 460800, 230400, 115200]

			# remove existing project

			_subprocess = subprocess.Popen(["ampy", "--port", _device_name, "ls"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			_standard_output, _standard_error = _subprocess.communicate()
			if _standard_error != b"":
				print(_standard_error)
			_output_lines = _standard_output.decode().split("\n")
			for _output_line in _output_lines:
				if _output_line != "" and _output_line != "/boot.py":
					print(f"Removing \"{_output_line}\"...")
					if "." in _output_line:
						_remove_subprocess = subprocess.Popen(["ampy", "--port", _device_name, "rm", _output_line], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					else:
						_remove_subprocess = subprocess.Popen(["ampy", "--port", _device_name, "rmdir", _output_line], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					_standard_output, _standard_error = _remove_subprocess.communicate()
					if _standard_error != b"":
						print(_standard_error)
					_remove_output_lines = _standard_output.decode().split("\n")
					for _remove_output_line in _remove_output_lines:
						if _remove_output_line != "":
							print(f"Output: {_remove_output_line}")

			# copy over project

			def _copy_directory_to_device(*, source_directory_path: str, destination_directory_name: str):
				_subprocess = subprocess.Popen(["ampy", "--port", _device_name, "put", source_directory_path, destination_directory_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				_standard_output, _standard_error = _subprocess.communicate()
				if _standard_error != b"":
					print(_standard_error)
				_output_lines = _standard_output.decode().split("\n")
				for _output_line in _output_lines:
					if _output_line != "":
						print(f"Output: {_output_line}")

			for _file_name in os.listdir(_project_directory):
				if _file_name != "venv" and not _file_name.startswith("."):
					_file_path = os.path.join(_project_directory, _file_name)
					if os.path.isfile(_file_path):
						print(f"Copying \"{_file_path}\"...")
						_copy_directory_to_device(
							source_directory_path=_file_path,
							destination_directory_name=_file_name
						)
					elif os.path.isdir(_file_path):
						print(f"Copying \"{_file_path}\"...")
						_copy_directory_to_device(
							source_directory_path=_file_path,
							destination_directory_name=_file_name
						)

			# copy over venv library modules of interest

			_useful_modules = [
				"austin_heller_repo"
			]

			_venv_directory_path = os.path.join(_project_directory, "venv")
			if not os.path.exists(_venv_directory_path):
				print(f"Cannot pull venv libraries due to missing venv directory at \"{_venv_directory_path}\".")
			else:
				_lib_directory_path = os.path.join(_venv_directory_path, "lib")
				_python_regex = re.compile("^python\d\.\d+(\.\d+)?$")
				for _file_name in os.listdir(_lib_directory_path):
					if _python_regex.search(_file_name) is not None:
						_python_directory_path = os.path.join(_lib_directory_path, _file_name)
						_site_packages_directory_path = os.path.join(_python_directory_path, "site-packages")

						for _useful_module in _useful_modules:
							_useful_module_directory_path = os.path.join(_site_packages_directory_path, _useful_module)
							if os.path.exists(_useful_module_directory_path):
								print(f"Copying \"{_useful_module_directory_path}\"...")
								_copy_directory_to_device(
									source_directory_path=_useful_module_directory_path,
									destination_directory_name=_useful_module
								)
						break
