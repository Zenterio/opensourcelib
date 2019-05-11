import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.test.utils import AssertDirExistsMixin
from debpacker.metapackage.metapackage import UnknownDistributionException, \
    _prepare_distribution_output_dirs


class TestPrepareDistributionOutputDir(TestCase, AssertDirExistsMixin):

    def setUp(self):
        self.test_dir_handle = TemporaryDirectory()
        self.test_dir = self.test_dir_handle.name
        self.dist = os.path.join(self.test_dir, 'dist')

    def tearDown(self):
        self.test_dir_handle.cleanup()

    def test_prepare_distribution_output_dir_unknown_dists(self):
        with self.assertRaises(UnknownDistributionException):
            _prepare_distribution_output_dirs(self.test_dir, 'unknown')

    def test_prepare_distribution_output_dir_ubuntu14(self):
        path = _prepare_distribution_output_dirs(self.test_dir, 'trusty')
        self.assertEqual(path, os.path.join(self.dist, 'trusty'))
        self.assert_dir_exists(path)

    def test_prepare_distribution_output_dir_ubuntu16(self):
        path = _prepare_distribution_output_dirs(self.test_dir, 'xenial')
        self.assertEqual(path, os.path.join(self.dist, 'xenial'))
        self.assert_dir_exists(path)

    def test_prepare_distribution_output_dir_no_specified_distribution(self):
        path = _prepare_distribution_output_dirs(self.test_dir, None)
        self.assertEqual(path, self.dist)
        self.assert_dir_exists(path)
