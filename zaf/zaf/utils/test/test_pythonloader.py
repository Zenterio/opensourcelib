import os
import sys
import unittest

from ..pythonloader import is_python_package, load_module_or_package, \
    load_submodules_and_subpackages


class TestLoadModuleOrPackage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.original_sys_path = sys.path
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))

    @classmethod
    def tearDownClass(cls):
        sys.path = cls.original_sys_path

    def test_raises_import_error_on_incorrect_path(self):
        with self.assertRaises(ImportError):
            load_module_or_package('does.not.exist')

    def test_raises_import_error_on_partially_correct_path(self):
        with self.assertRaises(ImportError):
            load_module_or_package('testpackage.nope')

    def test_raises_import_error_on_syntax_error(self):
        with self.assertRaises(ImportError):
            load_module_or_package('syntaxerror.this_file_contains_syntax_error')

    def test_syntax_error_on_import_includes_filename(self):
        with self.assertRaises(ImportError) as context:
            load_module_or_package('syntaxerror.this_file_contains_syntax_error')
        self.assertIn('this_file_contains_syntax_error.py', context.exception.msg)

    def test_syntax_error_on_import_includes_line_number(self):
        with self.assertRaises(ImportError) as context:
            load_module_or_package('syntaxerror.this_file_contains_syntax_error')
        self.assertIn('line 3', context.exception.msg)

    def test_syntax_error_on_import_includes_original_syntax_error(self):
        with self.assertRaises(ImportError) as context:
            load_module_or_package('syntaxerror.this_file_contains_syntax_error')
        self.assertIsInstance(context.exception.__cause__, SyntaxError)

    def test_can_load_a_package(self):
        package = load_module_or_package('testpackage.subpackage')
        self.assertTrue(is_python_package(package))

    def test_can_load_a_module(self):
        package = load_module_or_package('testpackage.this_file_contains_no_test_cases')
        self.assertFalse(is_python_package(package))


class TestLoadSubmodulesAndSubpackages(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.original_sys_path = sys.path
        sys.path.append(os.path.dirname(os.path.realpath(__file__)))

    @classmethod
    def tearDownClass(cls):
        sys.path = cls.original_sys_path

    def setUp(self):
        self.root_package = load_module_or_package('testpackage')
        self.all_modules_and_packages = load_submodules_and_subpackages(self.root_package)

    def test_loads_module(self):
        self.assertTrue(self._was_loaded('testpackage.this_file_contains_test_cases'))

    def test_load_subpackage(self):
        self.assertTrue(self._was_loaded('testpackage.subpackage'))

    def test_load_module_in_subpackage(self):
        self.assertTrue(
            self._was_loaded('testpackage.subpackage.this_file_contains_other_test_cases'))

    def _was_loaded(self, name):
        return any(thing.__name__ == name for thing in self.all_modules_and_packages)
