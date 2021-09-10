import sys
import os

sys.path.append(os.getcwd())

import subprocess
import serial.tools.list_ports
import esptool
from typing import List


_com_ports = serial.tools.list_ports.comports()

_device_names = []  # type: List[str]

for _com_port in _com_ports:
	_device_names.append(_com_port.device)

print(f"Select COM port")
for _device_name_index, _device_name in enumerate(_device_names):
	print(f"{_device_name_index}: {_device_name}")
_user_input = input("Device index: ")
if _user_input != "":
	_device_name_index = int(_user_input)
	esptool.main(['--port', _device_names[_device_name_index], 'flash_id'])
