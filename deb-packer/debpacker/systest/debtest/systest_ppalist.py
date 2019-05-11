import glob
import os
import unittest
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.test.utils import AssertFileExistsMixin, get_toolchain_test_data
from debpacker.systest.utils import AssertCorrectToolchainMixin, get_test_data, invoke_for_output, \
    prepare_template


class ToolchainListWithOnlyNewerVersionsSystest(TestCase, AssertFileExistsMixin,
                                                AssertCorrectToolchainMixin):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.test_root_handle = TemporaryDirectory()
        self.test_root = self.test_root_handle.name

    def tearDown(self):
        self.test_root_handle.cleanup()

    @unittest.skip('Will not work without a mock server that acts as PPA. Waiting for K2 as runner')
    def test_create_toolchains_from_file_definition(self):

        # URL1 has same version as in PPA
        # URL2 has newer version than in PPA
        # URL3 only exists for one of the dists in the PPA
        with prepare_template(get_test_data('toolchain_definitions_only_newer_versions.yaml'),
                              URL1=get_toolchain_test_data('tar.gz_archive.tar.gz'),
                              URL2=get_toolchain_test_data('toolchain_dir'),
                              URL3=get_toolchain_test_data('tgz_archive.tgz')) as definition_file:
            command = 'zdeb-packer toolchain-list --file {file} --only-newer-versions'.format(
                file=definition_file)
            invoke_for_output(command, cwd=self.test_root)
            self.assert_file_exists(os.path.join(self.test_root, 'zenterio-name2*.deb'))
            self.assert_file_exists(os.path.join(self.test_root, 'zenterio-name3*.deb'))
            self.assert_file_not_exists(os.path.join(self.test_root, 'zenterio-name1*.deb'))
            debs = glob.glob(os.path.join(self.test_root, '*.deb'))
            self.assertEqual(2, len(debs))
