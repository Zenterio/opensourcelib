import os
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from debpacker.common.test.utils import AssertFileRegexMixin, get_toolchain_test_data
from debpacker.common.utils import InvalidPackageNameException
from debpacker.toolchain import package_toolchain


class TestPackageToolchain(TestCase, AssertFileRegexMixin):

    def setUp(self):
        self.uri = get_toolchain_test_data('toolchain_dir')
        self.install_path = [
            '/tmp/install/some/path/to/new_dir_name/',
            '/tmp/install/some/other/path/to/other_dir_name/',
            '/tmp/install/some/third/path/to/dir_name/'
        ]
        self.test_dir_handle = TemporaryDirectory()
        self.test_dir = self.test_dir_handle.name
        self.out_dir = os.path.join(self.test_dir, 'dist')
        self.package_root = os.path.join(self.test_dir, 'output')

    def tearDown(self):
        self.test_dir_handle.cleanup()

    def test_package_toolchain_wrong_package_name(self):
        test_data = [
            'gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux',
            'IntelCE-i686-linux-2.6.39-gcc-4.5.1-uclibc-0.9.27',
            'intelce-i686-linux-2.6.39-gcc-4.5.1-uclibc 0.9.27',
            'IntelCE-i686-linux-2.6.39-gcc-4.5.1_uclibc 0.9.27',
            '@IntelCE-i686-linux-2.6.39%20gcc-4.5.1/uclibc-0.9.27-!'
        ]
        for package_name in test_data:
            expected = 'Package name "{name}" is invalid'.format(name=package_name)
            with self.assertRaisesRegex(InvalidPackageNameException, expected):
                package_toolchain(
                    self.uri, self.install_path, self.out_dir, package_name=package_name)

    def test_package_toolchain_integration_test(self):
        module = package_toolchain.__module__
        with patch(module+'.create_deb_binary_package', return_value='orig.deb') as create_deb_mock,\
                patch(module+'.move') as move_mock:
            package_toolchain(self.uri, self.install_path, self.out_dir, True, self.test_dir)
            create_deb_mock.assert_called_once_with(os.path.join(self.test_dir, 'output'))
            move_mock.assert_called_once_with('orig.deb', self.out_dir, override=True)
            self.assert_file_regex(
                os.path.join(self.package_root, 'debian', 'install'),
                'new_dir_name/ /tmp/install/some/path/to')
            self.assert_file_regex(
                os.path.join(self.package_root, 'debian', 'control'),
                'Package: zenterio-toolchain-dir')
            self.assert_file_regex(
                os.path.join(self.package_root, 'debian', 'install'),
                'other_dir_name/ /tmp/install/some/other/path/to')
            self.assert_file_regex(
                os.path.join(self.package_root, 'debian', 'install'),
                'dir_name/ /tmp/install/some/third/path/to')
            self.assert_file_regex(
                os.path.join(self.package_root, 'toolchain_dir', 'file'),
                'This is the file in toolchain_dir.')
