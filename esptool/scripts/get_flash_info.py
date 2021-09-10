import sys
import os

sys.path.append(os.getcwd())

import subprocess
import serial.tools.list_ports
import esptool
from typing import List


_com_ports = serial.tools.list_ports.comports()

_device_names = []  # type: List[str]

if False:
	print(f"_com_ports: {_com_ports}")
	for _com_port in _com_ports:
		print(f"_com_port: {_com_port}")
		print(f"{_com_port.device}")
		print(f"{_com_port.product}")
		print(f"{_com_port.name}")
		print(f"{_com_port.description}")
		print(f"{_com_port.hwid}")
		print(f"{_com_port.interface}")
		print(f"{_com_port.manufacturer}")
		print(f"{_com_port.pid}")
		print(f"{_com_port.serial_number}")

for _com_port in _com_ports:
	_device_names.append(_com_port.device)

print(f"Select COM port")
for _device_name_index, _device_name in enumerate(_device_names):
	print(f"{_device_name_index}: {_device_name}")
_user_input = input("Device index: ")
if _user_input != "":
	_device_name_index = int(_user_input)
	esptool.main(['--port', _device_names[_device_name_index], 'flash_id'])
