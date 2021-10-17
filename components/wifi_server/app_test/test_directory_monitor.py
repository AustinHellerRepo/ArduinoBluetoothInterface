from app.directory_monitor import DirectoryMonitor
import tempfile
import unittest
import os
import time
import threading
from datetime import datetime
from typing import List
import uuid


def create_random_file_name(directory_path: str, extension: str) -> str:
	_file_name = f"{uuid.uuid4()}{extension}"
	_file_path = os.path.join(directory_path, _file_name)
	with open(_file_path, "w") as _file_handle:
		pass
	return _file_path


class DirectoryMonitorTest(unittest.TestCase):

	def test_initialize_0(self):

		_temp_directory = tempfile.TemporaryDirectory()

		_is_directory_exists = os.path.exists(_temp_directory.name)

		self.assertEqual(True, _is_directory_exists)

		_directory_monitor = DirectoryMonitor(
			directory_path=_temp_directory.name,
			include_subdirectories=False,
			delay_between_checks_seconds=1.0
		)

		self.assertIsNotNone(_directory_monitor)

		_temp_directory.cleanup()

	def test_wait_0(self):
		# start, delay too late for change

		_temp_directory = tempfile.TemporaryDirectory()

		_is_directory_exists = os.path.exists(_temp_directory.name)

		self.assertEqual(True, _is_directory_exists)

		_directory_monitor = DirectoryMonitor(
			directory_path=_temp_directory.name,
			include_subdirectories=False,
			delay_between_checks_seconds=1.0
		)

		self.assertIsNotNone(_directory_monitor)

		_created_temp_file_paths = []  # type: List[str]

		def _change_directory_thread_method():
			time.sleep(1.1)
			_temp_file_path = create_random_file_name(_temp_directory.name, ".txt")
			_created_temp_file_paths.append(_temp_file_path)

		_change_directory_thread = threading.Thread(target=_change_directory_thread_method)

		_change_directory_thread.start()
		_directory_monitor.start()

		_start_time = datetime.utcnow()
		_directory_monitor.wait()
		_end_time = datetime.utcnow()

		_wait_seconds_total = (_end_time - _start_time).total_seconds()
		_rounded_wait_seconds_total = round(_wait_seconds_total * 10) / 10

		self.assertEqual(1.0, _rounded_wait_seconds_total)
		self.assertEqual(0, len(_created_temp_file_paths))

		time.sleep(1.0)

		for _temp_file_path in _created_temp_file_paths:
			os.unlink(_temp_file_path)

		_temp_directory.cleanup()

	def test_wait_1(self):
		# start, change just before delay, root directory

		_temp_directory = tempfile.TemporaryDirectory()

		_is_directory_exists = os.path.exists(_temp_directory.name)

		self.assertEqual(True, _is_directory_exists)

		_directory_monitor = DirectoryMonitor(
			directory_path=_temp_directory.name,
			include_subdirectories=False,
			delay_between_checks_seconds=1.0
		)

		self.assertIsNotNone(_directory_monitor)

		_created_temp_file_paths = []  # type: List[str]

		def _change_directory_thread_method():
			time.sleep(0.9)
			_temp_file_path = create_random_file_name(_temp_directory.name, ".txt")
			_created_temp_file_paths.append(_temp_file_path)

		_change_directory_thread = threading.Thread(target=_change_directory_thread_method)

		_change_directory_thread.start()
		_directory_monitor.start()

		_start_time = datetime.utcnow()
		_directory_monitor.wait()
		_end_time = datetime.utcnow()

		_wait_seconds_total = (_end_time - _start_time).total_seconds()
		_rounded_wait_seconds_total = round(_wait_seconds_total * 10) / 10

		self.assertEqual(2.0, _rounded_wait_seconds_total)
		self.assertEqual(1, len(_created_temp_file_paths))

		for _temp_file_path in _created_temp_file_paths:
			os.unlink(_temp_file_path)

		_temp_directory.cleanup()

	def test_wait_2(self):
		# start, change just before delay, multiple files, root directory

		_temp_directory = tempfile.TemporaryDirectory()

		_is_directory_exists = os.path.exists(_temp_directory.name)

		self.assertEqual(True, _is_directory_exists)

		_directory_monitor = DirectoryMonitor(
			directory_path=_temp_directory.name,
			include_subdirectories=False,
			delay_between_checks_seconds=1.0
		)

		self.assertIsNotNone(_directory_monitor)

		_created_temp_file_paths = []  # type: List[str]

		def _change_directory_thread_method():
			_sleep_seconds = 0.9
			for _index in range(10):
				time.sleep(_sleep_seconds)
				_sleep_seconds = 1.0
				_temp_file_path = create_random_file_name(_temp_directory.name, ".txt")
				_created_temp_file_paths.append(_temp_file_path)

		_change_directory_thread = threading.Thread(target=_change_directory_thread_method)

		_change_directory_thread.start()
		_directory_monitor.start()

		_start_time = datetime.utcnow()
		_directory_monitor.wait()
		_end_time = datetime.utcnow()

		_wait_seconds_total = (_end_time - _start_time).total_seconds()
		_rounded_wait_seconds_total = round(_wait_seconds_total * 10) / 10

		self.assertEqual(11.0, _rounded_wait_seconds_total)
		self.assertEqual(10, len(_created_temp_file_paths))

		for _temp_file_path in _created_temp_file_paths:
			os.unlink(_temp_file_path)

		_temp_directory.cleanup()

	def test_wait_3(self):
		# start, change just before delay, multiple files, ignore sub directories

		_temp_directory = tempfile.TemporaryDirectory()

		_is_directory_exists = os.path.exists(_temp_directory.name)

		self.assertEqual(True, _is_directory_exists)

		_directory_monitor = DirectoryMonitor(
			directory_path=_temp_directory.name,
			include_subdirectories=False,
			delay_between_checks_seconds=1.0
		)

		self.assertIsNotNone(_directory_monitor)

		_created_temp_file_paths = []  # type: List[str]

		def _change_directory_thread_method():
			try:
				_sleep_seconds = 0.5
				_directory_path = _temp_directory.name
				for _index in range(10):
					time.sleep(_sleep_seconds)
					_sleep_seconds = 1.0
					_temp_file_path = create_random_file_name(_directory_path, ".txt")
					_directory_path = os.path.join(_directory_path, str(uuid.uuid4()))
					os.mkdir(_directory_path)
					_created_temp_file_paths.append(_temp_file_path)
			except Exception as ex:
				print(f"ex: {ex}")

		_change_directory_thread = threading.Thread(target=_change_directory_thread_method)

		_change_directory_thread.start()
		_directory_monitor.start()

		_start_time = datetime.utcnow()
		_directory_monitor.wait()
		_end_time = datetime.utcnow()

		_wait_seconds_total = (_end_time - _start_time).total_seconds()
		_rounded_wait_seconds_total = round(_wait_seconds_total * 10) / 10

		time.sleep(9.0)

		self.assertEqual(2.0, _rounded_wait_seconds_total)
		self.assertEqual(10, len(_created_temp_file_paths))

		for _temp_file_path in _created_temp_file_paths:
			os.unlink(_temp_file_path)

		_temp_directory.cleanup()

	def test_wait_4(self):
		# start, change just before delay, multiple files, inspect sub directories

		_temp_directory = tempfile.TemporaryDirectory()

		_is_directory_exists = os.path.exists(_temp_directory.name)

		self.assertEqual(True, _is_directory_exists)

		_directory_monitor = DirectoryMonitor(
			directory_path=_temp_directory.name,
			include_subdirectories=True,
			delay_between_checks_seconds=1.0
		)

		self.assertIsNotNone(_directory_monitor)

		_created_temp_file_paths = []  # type: List[str]

		def _change_directory_thread_method():
			try:
				_sleep_seconds = 0.5
				_directory_path = _temp_directory.name
				for _index in range(10):
					time.sleep(_sleep_seconds)
					_sleep_seconds = 1.0
					_temp_file_path = create_random_file_name(_directory_path, ".txt")
					_directory_path = os.path.join(_directory_path, str(uuid.uuid4()))
					os.mkdir(_directory_path)
					_created_temp_file_paths.append(_temp_file_path)
			except Exception as ex:
				print(f"ex: {ex}")

		_change_directory_thread = threading.Thread(target=_change_directory_thread_method)

		_change_directory_thread.start()
		_directory_monitor.start()

		_start_time = datetime.utcnow()
		_directory_monitor.wait()
		_end_time = datetime.utcnow()

		_wait_seconds_total = (_end_time - _start_time).total_seconds()
		_rounded_wait_seconds_total = round(_wait_seconds_total * 4) / 4

		self.assertEqual(11.0, _rounded_wait_seconds_total)
		self.assertEqual(10, len(_created_temp_file_paths))

		for _temp_file_path in _created_temp_file_paths:
			os.unlink(_temp_file_path)

		_temp_directory.cleanup()


if __name__ == "__main__":
	unittest.main()
