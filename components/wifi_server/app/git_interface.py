from __future__ import annotations
import os
from app.directory_monitor import DirectoryMonitor


class GitInterface():

	def __init__(self):

		pass

	@staticmethod
	def clone(*, git_repository_url: str, git_clone_directory_path: str, delay_clone_completed_polling_seconds: float):

		try:
			os.stat(git_clone_directory_path)
		except Exception as ex:
			if "No such file or directory" in str(ex):
				# normal
				os.mkdir(git_clone_directory_path)
			elif "[Errno 2] ENOENT" in str(ex):
				# micropython
				os.mkdir(git_clone_directory_path)
			else:
				raise ex

		os.chdir(git_clone_directory_path)

		os.system("git clone " + git_repository_url)

		_directory_monitor = DirectoryMonitor(
			directory_path=git_clone_directory_path,
			include_subdirectories=True,
			delay_between_checks_seconds=delay_clone_completed_polling_seconds
		)

		_directory_monitor.start()
		_directory_monitor.wait()
