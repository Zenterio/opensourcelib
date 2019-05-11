import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.test.utils import AssertFileContainsMixin, create_file
from debpacker.toolchain.toolchain import _create_symlinks


class TestCreateSymlinks(TestCase, AssertFileContainsMixin):

    def setUp(self):
        test_root_handle = TemporaryDirectory()
        self.addCleanup(test_root_handle.cleanup)
        self.test_root = test_root_handle.name
        self.toolchain_path = os.path.join(self.test_root, 'toolchain')
        self.file_path = os.path.join(self.toolchain_path, 'file')
        create_file(self.file_path, 'file_content')

    def test_single_path_with_same_destination(self):
        _create_symlinks(self.test_root, 'toolchain', ['toolchain'])
        self.assert_file_contains(os.path.join(self.test_root, 'toolchain', 'file'), 'file_content')

    def test_multiple_paths_with_same_destination(self):
        paths = ['toolchain', 'toolchain']
        _create_symlinks(self.test_root, 'toolchain', paths)
        self.assert_file_contains(self.file_path, 'file_content')
        self.assertEqual(os.listdir(self.test_root), ['toolchain'])

    def test_single_path_with_different_destination(self):
        paths = ['toolchain_variant']
        _create_symlinks(self.test_root, 'toolchain', paths)
        self.assert_file_contains(
            os.path.join(self.test_root, 'toolchain_variant', 'file'), 'file_content')
        self.assertEqual(
            list(sorted(os.listdir(self.test_root))), ['toolchain', 'toolchain_variant'])

    def test_multiple_paths_with_same_and_different_destination(self):
        paths = ['toolchain', 'toolchain1', 'toolchain', 'toolchain2', 'toolchain3']
        _create_symlinks(self.test_root, 'toolchain', paths)
        self.assert_file_contains(os.path.join(self.test_root, 'toolchain', 'file'), 'file_content')
        self.assert_file_contains(
            os.path.join(self.test_root, 'toolchain1', 'file'), 'file_content')
        self.assert_file_contains(
            os.path.join(self.test_root, 'toolchain2', 'file'), 'file_content')
        self.assert_file_contains(
            os.path.join(self.test_root, 'toolchain3', 'file'), 'file_content')
        self.assertEqual(
            list(sorted(os.listdir(self.test_root))),
            ['toolchain', 'toolchain1', 'toolchain2', 'toolchain3'])
