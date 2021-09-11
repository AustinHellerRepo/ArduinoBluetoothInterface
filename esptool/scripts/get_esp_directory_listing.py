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
	print(f"Select COM port")
	for _device_name_index, _device_name in enumerate(_device_names):
		print(f"{_device_name_index}: {_device_name}")
	_user_input = input("Device index: ")
	if _user_input != "":
		_device_name_index = int(_user_input)
		_device_name = _device_names[_device_name_index]

		_baud_rates = [921600, 460800, 230400, 115200]

		_directories = []  # type: List[str]
		_directories.append("/")

		while len(_directories) != 0:
			_directory = _directories.pop(0)
			_subprocess = subprocess.Popen(["ampy", "--port", _device_name, "ls", _directory], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			_standard_output, _standard_error = _subprocess.communicate()
			_output_lines = _standard_output.decode().split("\n")
			for _output_line in _output_lines:
				if _output_line != "":
					print(f"{_directory} {_output_line}")
					if "." not in _output_line:
						_directories.append(_output_line)
			if _standard_error != b"":
				print(f"_standard_error: {_standard_error}")

		if False:
			_data = ampy.cli.cli(["--port", _device_name, "ls"])
			print(f"_data: {_data}")

		if False:
			print("test1")
			with StringIO() as _stdout:
				with redirect_stdout(_stdout):
					print("starting...")
					ampy.cli.cli(["--port", _device_name, "ls"])
					print("stopping...")
					sys.stdout.flush()
				_output_lines = _stdout.getvalue()
				print(f"_output_lines: {_output_lines}")
				for _output_line in _output_lines:
					print(_output_line)
				print("test2")
			print("test3")