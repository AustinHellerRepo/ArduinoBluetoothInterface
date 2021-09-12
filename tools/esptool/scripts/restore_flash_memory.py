import sys
import os

sys.path.append(os.getcwd())

import subprocess
import serial.tools.list_ports
import esptool
from typing import List
from io import StringIO
import re


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
	_restore_file_path = input("Restore file path: ")
	if _restore_file_path != "":
		print(f"Select COM port")
		for _device_name_index, _device_name in enumerate(_device_names):
			print(f"{_device_name_index}: {_device_name}")
		_user_input = input("Device index: ")
		if _user_input != "":
			_device_name_index = int(_user_input)
			_device_name = _device_names[_device_name_index]
			with OutputCapture() as _output_lines:
				esptool.main(['--port', _device_name, 'flash_id'])
			for _output_line in _output_lines:
				if _output_line.startswith("Detected flash size: "):
					_flash_size_string = _output_line.split(": ")[1]
					print(f"_flash_size_string: \"{_flash_size_string}\"")
					_flash_size_integer = 1
					if _flash_size_string[-2] == "K":
						_flash_size_integer *= 1024
					elif _flash_size_string[-2] == "M":
						_flash_size_integer *= (1024**2)
					elif _flash_size_string[-3] == "G":
						_flash_size_integer *= (1024**3)
					else:
						_error = f"Unexpected size: \"{_flash_size_string}\"."
						print(_error)
						raise Exception(_error)

					if _flash_size_string[-1] == "b":
						_flash_size_integer = int(_flash_size_integer / 8)

					_flash_size_value = int(re.findall("^\d+", _flash_size_string)[0])
					_flash_size_integer *= _flash_size_value

					# check that flash memory bin file is correct size

					_restore_file_size = os.path.getsize(_restore_file_path)

					if _restore_file_size != _flash_size_integer:
						_error = f"Unexpected mismatch between file size and flash memory. Expected {_flash_size_integer}, found {_restore_file_size} file size."
						print(_error)
						raise Exception(_error)

					_flash_size_hex = str(hex(_flash_size_integer))

					print(f"_flash_size_hex: {_flash_size_hex}")

					_baud_rates = [921600, 460800, 230400, 115200]

					for _baud_rate in _baud_rates:
						try:
							esptool.main(["--port", _device_name, "--baud", str(_baud_rate), "--before", "default_reset", "--after", "hard_reset", "write_flash", "-z", "--flash_mode", "dio", "--flash_freq", "80m", "--flash_size", "detect", "0x0", _restore_file_path])
							break
						except Exception as ex:
							print(f"ex: {ex}")
							if "Corrupt data" in str(ex):
								print(f"Testing next baud rate after {_baud_rate} failed...")
							else:
								break
