from os.path import join
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.test.utils import AssertFileContainsMixin, AssertFileRegexMixin
from debpacker.toolchain.toolchain import _import_debian_template


class TestImportDebianTemplate(TestCase, AssertFileContainsMixin, AssertFileRegexMixin):

    def setUp(self):
        pass

    def test_import_template(self):
        with TemporaryDirectory() as tmp_dir:
            path = _import_debian_template(
                tmp_dir, 'package-name', 'toolchain1.0.2', '/install/path', 'test-version',
                ['test-depends'])
            self.assertEqual(path, join(tmp_dir, 'debian'))
            self.assert_file_contains(join(path, 'compat'), '9')
            self.assert_file_regex(
                join(path, 'changelog'), r'package-name \(test-version\) unstable; urgency=low')
            self.assert_file_regex(join(path, 'control'), r'Source: package-name')
            self.assert_file_regex(join(path, 'control'), r'Package: package-name')
            self.assert_file_regex(join(path, 'control'), r'Description: Toolchain toolchain1.0.2')
            self.assert_file_regex(
                join(path, 'control'), r' This toolchain is installed at /install/path')
            self.assert_file_regex(join(path, 'control'), r'Depends: test-depends')
