import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.templatehandling import ConflictStrategy, import_template_dir
from debpacker.common.test.utils import AssertFileExistsMixin, AssertFileRegexMixin, get_test_data


class TestImportTemplateDir(TestCase, AssertFileExistsMixin, AssertFileRegexMixin):

    def setUp(self):
        self.template = get_test_data('template_dir')
        self.template_kwargs = {
            'TEMPLATE1': 'first replacement',
            'TEMPLATE2': 'second replacement',
            'TEMPLATE3': 'third replacement',
        }

    def test_import_template_dir(self):
        with TemporaryDirectory() as test_dir:
            import_template_dir(self.template, test_dir, **self.template_kwargs)
            file1 = os.path.join(test_dir, 'template_dir', 'file1')
            file2 = os.path.join(test_dir, 'template_dir', 'file2')
            self.assert_file_exists(os.path.join(test_dir, 'template_dir'))
            self.assert_file_regex(file1, r'Some text with template1: first replacement')
            self.assert_file_regex(
                file1, r'Some more text with second replacement and after more text')
            self.assert_file_regex(
                file2, r'After blank lines comes some templates '
                r'\[first replacement, second replacement, third replacement\]')

    def test_import_template_dir_can_fail_when_dir_exists(self):
        with TemporaryDirectory() as test_dir:
            os.makedirs(os.path.join(test_dir, 'template_dir'))
            with self.assertRaises(FileExistsError):
                import_template_dir(
                    self.template,
                    test_dir,
                    conflict_strategy=ConflictStrategy.fail,
                    **self.template_kwargs)
