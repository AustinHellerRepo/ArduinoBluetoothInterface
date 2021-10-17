import threading
from typing import Dict
import os
import time


class DirectoryMonitor():

	def __init__(self, *, directory_path: str, include_subdirectories: bool, delay_between_checks_seconds: float):

		self.__directory_path = directory_path
		self.__include_subdirectories = include_subdirectories
		self.__delay_between_checks_seconds = delay_between_checks_seconds

		self.__monitor_thread = None  # type: threading.Thread
		self.__monitor_thread_semaphore = threading.Semaphore()
		self.__is_monitor_thread_running = False
		self.__wait_semaphore = threading.Semaphore()

	def start(self):

		self.__monitor_thread_semaphore.acquire()
		if self.__is_monitor_thread_running:
			self.__monitor_thread_semaphore.release()
			raise Exception(f"Cannot begin monitoring without first starting.")
		else:
			self.__is_monitor_thread_running = True
			self.__monitor_thread = threading.Thread(target=self.__monitor_thread_method)
			self.__wait_semaphore.acquire()
			self.__monitor_thread.start()
			self.__monitor_thread_semaphore.release()

	def wait(self):
		self.__wait_semaphore.acquire()
		self.__wait_semaphore.release()

	def __monitor_thread_method(self):

		_previous_file_sizes_per_file_path = {}  # type: Dict[str, int]
		while self.__is_monitor_thread_running:

			_is_new_file_discovered = False
			_is_existing_file_size_different = False
			_is_file_missing = False
			if self.__directory_path not in _previous_file_sizes_per_file_path.keys():
				_is_new_file_discovered = True
			_current_file_sizes_per_file_path = {
				self.__directory_path: None
			}  # type: Dict[str, int]
			_pending_directories = [
				self.__directory_path
			]
			while len(_pending_directories) != 0:
				_directory_path = _pending_directories.pop(0)
				for _file_name in os.listdir(_directory_path):
					_file_path = os.path.join(_directory_path, _file_name)
					if os.path.isdir(_file_path):
						_is_file = False
						_file_size = None
					else:
						_is_file = True
						_file_size = os.stat(_file_path).st_size
					if _file_path not in _previous_file_sizes_per_file_path.keys():
						_is_new_file_discovered = True
					elif _is_file and _previous_file_sizes_per_file_path[_file_path] != _file_size:
						_is_existing_file_size_different = True

					_current_file_sizes_per_file_path[_file_path] = _file_size
					if not _is_file and self.__include_subdirectories:
						_pending_directories.append(_file_path)
			for _file_path in _previous_file_sizes_per_file_path:
				if _file_path not in _current_file_sizes_per_file_path.keys():
					_is_file_missing = True
					break
			if _is_new_file_discovered or _is_existing_file_size_different or _is_file_missing:
				_previous_file_sizes_per_file_path = _current_file_sizes_per_file_path
				_current_file_sizes_per_file_path = None
				time.sleep(self.__delay_between_checks_seconds)
			else:
				self.__wait_semaphore.release()
				self.__is_monitor_thread_running = False
