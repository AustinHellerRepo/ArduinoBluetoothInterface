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
	_firmware_file_path = input("Firmware file path: ")
	if _firmware_file_path != "":
		print(f"Select COM port")
		for _device_name_index, _device_name in enumerate(_device_names):
			print(f"{_device_name_index}: {_device_name}")
		_user_input = input("Device index: ")
		if _user_input != "":
			_device_name_index = int(_user_input)
			_device_name = _device_names[_device_name_index]

			print("Clearing firmware...")
			esptool.main(["--port", _device_name, "erase_flash"])

			_baud_rates = [921600, 460800, 230400, 115200]

			for _baud_rate in _baud_rates:
				try:
					esptool.main(["--port", _device_name, "--baud", str(_baud_rate), "write_flash", "-z", "0x1000", _firmware_file_path])
					break
				except Exception as ex:
					print(f"ex: {ex}")
					if "Corrupt data" in str(ex):
						print(f"Testing next baud rate after {_baud_rate} failed...")
					else:
						break
