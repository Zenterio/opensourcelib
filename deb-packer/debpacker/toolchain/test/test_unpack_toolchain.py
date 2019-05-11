import os
import shutil
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.test.utils import AssertFileContainsMixin, get_toolchain_test_data
from debpacker.toolchain.toolchain import _unpack_toolchain


class TestUnpackToolchain(TestCase, AssertFileContainsMixin):

    def setUp(self):
        self.tar_gz_archive = get_toolchain_test_data('tar.gz_archive.tar.gz')
        self.tgz_archive = get_toolchain_test_data('tgz_archive.tgz')
        self.directory = get_toolchain_test_data('toolchain_dir')

    def test_unpack_tar_gz(self):
        with TemporaryDirectory() as tmp_dir:
            unpack_dir = os.path.join(tmp_dir, 'tar.gz_archive')
            archive_name = _unpack_toolchain(self.tar_gz_archive, unpack_dir)
            self.assertEqual(archive_name, 'tar.gz_archive')
            self.assert_file_contains(
                os.path.join(unpack_dir, 'file'), 'This is the tar.gz archive.\n')

    def test_unpack_tgz(self):
        with TemporaryDirectory() as tmp_dir:
            unpack_dir = os.path.join(tmp_dir, 'tgz_archive')
            archive_name = _unpack_toolchain(self.tgz_archive, unpack_dir)
            self.assertEqual(archive_name, 'tgz_archive')
            self.assert_file_contains(
                os.path.join(unpack_dir, 'file'), 'This is the tgz archive.\n')

    def test_unpack_tgz_wit_different_name(self):
        with TemporaryDirectory() as tmp_dir:
            unpack_dir = os.path.join(tmp_dir, 'tgz_archive_different')
            archive_name = _unpack_toolchain(self.tgz_archive, unpack_dir)
            self.assertEqual(archive_name, 'tgz_archive')
            self.assert_file_contains(
                os.path.join(unpack_dir, 'file'), 'This is the tgz archive.\n')

    def test_unpack_directory(self):
        with TemporaryDirectory() as tmp_dir:
            directory = os.path.join(tmp_dir, 'toolchain_dir')
            shutil.copytree(self.directory, directory)
            unpack_dir = os.path.join(tmp_dir, 'toolchain_dir')
            archive_name = _unpack_toolchain(directory, unpack_dir)
            self.assertEqual(archive_name, 'toolchain_dir')
            self.assert_file_contains(
                os.path.join(unpack_dir, 'file'), 'This is the file in toolchain_dir.')
