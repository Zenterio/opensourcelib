import glob
import logging
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.test.utils import AssertFileContainsMixin, AssertFileExistsMixin, \
    AssertFileNotExistsMixin, AssertFileRegexMixin
from debpacker.systest.utils import get_test_data, invoke_for_output, uninstall

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class MetapackageSystest(TestCase, AssertFileExistsMixin, AssertFileRegexMixin,
                         AssertFileContainsMixin, AssertFileNotExistsMixin):
    installed_packages = ['zenterio-metapackage1', 'zenterio-metapackage2']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        for package in cls.installed_packages:
            uninstall(package)

    def setUp(self):
        self.test_root_handle = TemporaryDirectory()
        self.test_root = self.test_root_handle.name

    def tearDown(self):
        self.test_root_handle.cleanup()

    def assert_metapackage_can_be_installed(
            self, package_root, *expected_outputs, expected_exit_code=0, deb_glob=None):
        if not deb_glob:
            deb_glob = os.path.join(package_root, 'dist', '*.deb')
        deb_file = glob.glob(deb_glob)[0]
        self.assertRegex(
            os.path.basename(deb_file), r'zenterio-.*_1\.0\.0.*_all\.deb',
            'Debian file name not correct formatted')
        command = 'sudo dpkg -i {debfile}'.format(debfile=deb_file)
        output = invoke_for_output(command, expected_exit_code=expected_exit_code, cwd=package_root)

        for expected_output in expected_outputs:
            self.assertIn(expected_output, output)

    def test_create_metapackage(self):
        infile = get_test_data('metapackage_no_nonexisting_dependencies.yaml')
        command = 'zdeb-packer -v metapackage {infile}'.format(infile=infile)
        invoke_for_output(command, cwd=self.test_root)
        self.assert_metapackage_can_be_installed(
            self.test_root, 'Unpacking zenterio-metapackage2 (1.0.0) ...',
            'Setting up zenterio-metapackage2 (1.0.0) ...')

    def test_create_metapackage_with_one_unresolvable_dependency(self):
        infile = get_test_data('metapackage_one_nonexisting_dependency.yaml')
        command = 'zdeb-packer -v metapackage {infile}'.format(infile=infile)
        invoke_for_output(command, cwd=self.test_root)
        self.assert_metapackage_can_be_installed(
            self.test_root,
            'dpkg: error processing package zenterio-metapackage1 (--install):\n '
            'dependency problems - leaving unconfigured\n'
            'Errors were encountered while processing:\n '
            'zenterio-metapackage1',
            expected_exit_code=1)

    def test_to_create_multiple_metapackages(self):
        infile1 = get_test_data('metapackage_multiple_distributions_trusty_and_xenial.yaml')
        infile2 = get_test_data('metapackage_multiple_only_xenial_distribution.yaml')
        invoke_for_output(
            'zdeb-packer metapackage {infile}'.format(infile=infile1), cwd=self.test_root)
        invoke_for_output(
            'zdeb-packer metapackage {infile}'.format(infile=infile2), cwd=self.test_root)
        self.assert_file_exists(
            os.path.join(self.test_root, 'dist', 'trusty', 'metapackage-trusty-and-xenial*.deb'))
        self.assert_file_exists(
            os.path.join(self.test_root, 'dist', 'xenial', 'metapackage-trusty-and-xenial*.deb'))
        self.assert_file_exists(
            os.path.join(self.test_root, 'dist', 'xenial', 'metapackage-xenial*.deb'))
