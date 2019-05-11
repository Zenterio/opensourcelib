import os
from shutil import Error
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.test.utils import AssertFileContainsMixin, AssertFileExistsMixin, \
    AssertFileNotExistsMixin
from debpacker.common.utils import move


class TestMove(TestCase, AssertFileExistsMixin, AssertFileNotExistsMixin, AssertFileContainsMixin):

    def setUp(self):
        self.dir1 = TemporaryDirectory()
        self.dir2 = TemporaryDirectory()
        self.file1 = os.path.join(self.dir1.name, 'file1')
        self.file2 = os.path.join(self.dir2.name, 'file2')
        with open(self.file1, 'w') as file:
            file.write('file1')
        with open(self.file2, 'w') as file:
            file.write('file2')

    def tearDown(self):
        self.dir1.cleanup()
        self.dir2.cleanup()

    def test_move_file(self):
        move(self.file1, self.dir2.name)
        self.assert_file_exists(os.path.join(self.dir2.name, 'file2'))
        self.assert_file_not_exists(self.file1)

    def test_move_file_to_dir_containing_a_file_with_the_same_name(self):
        new_name = os.path.join(self.dir1.name, 'file2')
        move(self.file1, new_name)
        with self.assertRaises(Error):
            move(new_name, self.dir2.name)

    def test_move_file_with_override(self):
        new_name = os.path.join(self.dir1.name, 'file2')
        move(self.file1, new_name)
        move(new_name, self.dir2.name, override=True)
        self.assert_file_contains(self.file2, 'file1')
