import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.preparedassets import OutputExists, prepare_output_dir


class TestPrepareOutputDir(TestCase):

    def setUp(self):
        self.test_root_handle = TemporaryDirectory()
        self.test_root = self.test_root_handle.name
        self.file = os.path.join(self.test_root, 'file')
        open(self.file, 'w').close()

    def tearDown(self):
        self.test_root_handle.cleanup()

    def test_prepare_output_dir_which_is_a_file(self):
        with self.assertRaises(OutputExists):
            prepare_output_dir(self.file)

    def test_prepare_output_dir_which_is_a_dir(self):
        prepare_output_dir(self.test_root)
        self.assertEqual(len(os.listdir(self.test_root)), 1)

    def test_prepare_output_dir_which_does_not_exist(self):
        path = os.path.join(self.test_root, 'new_dir')
        prepare_output_dir(path)
        self.assertTrue(os.path.isdir(path))
