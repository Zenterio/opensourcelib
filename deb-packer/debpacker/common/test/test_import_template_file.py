import logging
import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from debpacker.common.templatehandling import ConflictStrategy, import_template_file
from debpacker.common.test.utils import AssertFileRegexMixin, create_file, get_test_data


class TestImportTemplateFile(TestCase, AssertFileRegexMixin):

    def setUp(self):
        self.test_root_handle = TemporaryDirectory()
        self.test_root = self.test_root_handle.name
        self.template_file1 = get_test_data('template_dir', 'file1')
        self.template_kwargs = {'TEMPLATE1': 'value1', 'TEMPLATE2': 'value2'}
        self.expected_lines = [
            'Some text with template1: value1',
            'Some more text with value2 and after more text',
        ]

    def tearDown(self):
        self.test_root_handle.cleanup()

    def assert_file_contain_lines(self, path, lines):
        for line in lines:
            self.assert_file_regex(path, line)

    def test_import_template_file(self):
        result = import_template_file(self.template_file1, self.test_root, **self.template_kwargs)
        self.assertEqual(os.path.join(self.test_root, 'file1'), result)
        self.assert_file_contain_lines(result, self.expected_lines)

    def test_import_template_file_exists_so_skip(self):
        create_file(os.path.join(self.test_root, 'file1'), 'file1')
        with self.assertLogs(logging.getLogger(), logging.DEBUG):
            result = import_template_file(
                self.template_file1, self.test_root, ConflictStrategy.skip)
            self.assertEqual(os.path.join(self.test_root, 'file1'), result)
            self.assert_file_regex(result, 'file1')

    def test_import_template_file_exists_so_replace(self):
        create_file(os.path.join(self.test_root, 'file1'), 'file1')
        result = import_template_file(
            self.template_file1, self.test_root, ConflictStrategy.replace_files,
            **self.template_kwargs)
        self.assertEqual(os.path.join(self.test_root, 'file1'), result)
        self.assert_file_contain_lines(result, self.expected_lines)

    def test_import_template_file_exists_so_fail(self):
        create_file(os.path.join(self.test_root, 'file1'), 'file1')
        with self.assertRaises(FileExistsError):
            result = import_template_file(
                self.template_file1, self.test_root, ConflictStrategy.fail)
            self.assertEqual(os.path.join(self.test_root, 'file1'), result)
            self.assert_file_regex(result, 'file1')
