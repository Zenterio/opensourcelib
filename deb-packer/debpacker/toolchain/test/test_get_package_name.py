from unittest import TestCase

from debpacker.toolchain.toolchain import _get_package_name


class TestGetPackageName(TestCase):

    def test_fix_underscore(self):
        expected = 'zenterio-intel-i686-linux-2.6.39-gcc-4.5.1-uclibc-0.9.27'
        actual = _get_package_name('intel-i686_linux-2.6.39_gcc-4.5.1_uclibc-0.9.27')
        self.assertEqual(expected, actual)

    def test_fix_upper_case_characters(self):
        expected = 'zenterio-intelce-i686'
        actual = _get_package_name('IntelCE-i686')
        self.assertEqual(expected, actual)

    def test_fix_single_compress_format(self):
        expected = 'zenterio-package'
        actual = _get_package_name('package.tgz')
        self.assertEqual(expected, actual)

    def test_fix_multiple_extensions_compress_format(self):
        expected = 'zenterio-package'
        actual = _get_package_name('package.tar.gz')
        self.assertEqual(expected, actual)

    def test_fix_tar_bz2_format(self):
        expected = 'zenterio-package'
        actual = _get_package_name('package.tar.bz2')
        self.assertEqual(expected, actual)

    def test_fix_all(self):
        expected = 'zenterio-intelce-i686-linux-2.6.39-gcc-4.5.1-uclibc-0.9.27'
        actual = _get_package_name('IntelCE-i686_linux-2.6.39_gcc-4.5.1_uclibc-0.9.27')
        self.assertEqual(expected, actual)
