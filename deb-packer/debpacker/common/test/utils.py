import glob
import os

from debpacker.common.utils import get_all_files, get_file_relative_root


class AssertFileContainsMixin:

    def assert_file_contains(self, path, content):
        with open(path) as file:
            self.assertEqual(file.read(), content, 'for file {path}'.format(path=path))


class AssertDirExistsMixin:

    def assert_dir_exists(self, path):
        self.assertTrue(os.path.isdir(path), 'No directory at {path}'.format(path=path))


class AssertFileExistsMixin:

    def assert_file_exists(self, pattern):
        matches = glob.glob(pattern)
        self.assertFalse(
            len(matches) == 0, 'No file found for glob "{pattern}"'.format(pattern=pattern))
        self.assertTrue(
            len(matches) == 1, 'More than one file find for glob "{pattern}" -> {files}'.format(
                pattern=pattern, files=matches))


class AssertFileRegexMixin:

    def assert_file_regex(self, path, expected_regex):
        with open(path) as file:
            self.assertRegex(file.read(), expected_regex)


class AssertFileNotExistsMixin:

    def assert_file_not_exists(self, path):
        self.assertFalse(os.path.exists(path), 'for file {path}'.format(path=path))


def get_test_data(*name):
    return get_file_relative_root(__file__, 'data', *name)


def get_toolchain_test_data(name):
    return get_test_data('toolchains', name)


def print_dir(root):
    for file in get_all_files(root):
        print(file)


def create_file(path, content=''):
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    with open(path, 'w') as file:
        file.write(content)
