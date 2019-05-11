import os
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from debpacker.common.test.utils import AssertFileRegexMixin
from debpacker.metapackage import create_metapackage
from debpacker.metapackage.configreader import PackageConfig


class TestCreateMetapackage(TestCase, AssertFileRegexMixin):

    def setUp(self):
        self.test_dir_handle = TemporaryDirectory()
        self.test_dir = self.test_dir_handle.name
        long_description = """
This is the long description
with contains multiple lines.
Some of which does not have have
 space after the newline
        """
        self.config = PackageConfig(
            name='zenterio-test-metapackage',
            version='',
            long_description=long_description,
            short_description='This is just one line',
            dependencies=['dep1'],
            architecture='',
            distributions='')
        self.package_root = os.path.join(self.test_dir, 'output')

    def tearDown(self):
        self.test_dir_handle.cleanup()

    def test_create_metapackage(self):
        module = create_metapackage.__module__
        with patch(module + '.create_deb_equivs_package', return_value='file.deb') as create_deb_mock, \
                patch(module + '.move') as move_mock:
            create_metapackage(self.test_dir, self.test_dir, True, self.config)

            template_file = os.path.join(self.test_dir, 'output', 'debian_template.equivs')
            create_deb_mock.assert_called_once_with(template_file)
            move_mock.assert_called_once_with(
                'file.deb', os.path.join(self.test_dir, 'dist'), override=True)
            self.assert_file_regex(template_file, 'Package: zenterio-test-metapackage')
            self.assert_file_regex(template_file, 'Depends: dep1')
            self.assert_file_regex(template_file, 'Description: This is just one line')
            self.assert_file_regex(template_file, ' This is the long description')
            self.assert_file_regex(template_file, ' with contains multiple lines.')
            self.assert_file_regex(template_file, ' Some of which does not have have')
            self.assert_file_regex(template_file, '  space after the newline')
