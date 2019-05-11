import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.test.utils import AssertDirExistsMixin, AssertFileContainsMixin, \
    AssertFileExistsMixin, get_toolchain_test_data
from debpacker.toolchain.toolchain import _get_toolchain


class TestGetToolchain(TestCase, AssertFileExistsMixin, AssertFileContainsMixin,
                       AssertDirExistsMixin):

    def setUp(self):
        self.dir_path = get_toolchain_test_data('toolchain_dir')
        self.path = get_toolchain_test_data('tar.gz_archive.tar.gz')
        self.uri = 'file://{path}'.format(path=self.path)

    def test_get_tar_gz_archive_by_file_uri(self):
        with TemporaryDirectory() as tmp_dir:
            path = _get_toolchain(self.uri, tmp_dir)
            self.assertEqual(path, os.path.join(tmp_dir, 'tar.gz_archive.tar.gz'))
            self.assert_file_exists(path)

    def test_get_tar_gz_archive_by_file_path(self):
        with TemporaryDirectory() as tmp_dir:
            path = _get_toolchain(self.path, tmp_dir)
            self.assertEqual(path, os.path.join(tmp_dir, 'tar.gz_archive.tar.gz'))
            self.assert_file_exists(path)

    def test_get_directory_by_file_path(self):
        with TemporaryDirectory() as tmp_dir:
            path = _get_toolchain(self.dir_path, tmp_dir)
            self.assertEqual(path, os.path.join(tmp_dir, 'toolchain_dir'))
            self.assert_dir_exists(path)
            self.assert_file_contains(
                os.path.join(path, 'file'), 'This is the file in toolchain_dir.')
