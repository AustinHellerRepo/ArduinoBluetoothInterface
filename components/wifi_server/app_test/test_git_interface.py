from app.git_interface import GitInterface
import unittest
import tempfile
import os


class GitInterfaceTest(unittest.TestCase):

	def test_initialize_0(self):

		_git_interface = GitInterface()

	def test_clone_0(self):

		_temp_directory = tempfile.TemporaryDirectory()

		GitInterface.clone(
			git_repository_url="https://github.com/AustinHellerRepo/TestDeviceModule",
			git_clone_directory_path=_temp_directory.name,
			delay_clone_completed_polling_seconds=0.1
		)

		_expected_file_names = [
			".gitignore",
			"LICENSE",
			"module.py",
			"requirements.txt"
		]

		for _expected_file_name in _expected_file_names:
			_expected_file_path = os.path.join(_temp_directory.name, "TestDeviceModule", _expected_file_name)
			_is_file_exists = os.path.exists(_expected_file_path)
			self.assertEqual(True, _is_file_exists)

		_temp_directory.cleanup()


if __name__ == "__main__":
	unittest.main()
