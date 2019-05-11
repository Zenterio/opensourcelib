import sys
from io import StringIO
from unittest import TestCase

from ..wizard import _camel_case_validator, _email_validator, _escape_single_quote_validator, \
    _setuptools_version_validator, _string_length_validator, run_generic_addon_wizard


class TestStringLengthValidator(TestCase):

    def test_valid_string(self):
        assert 'abc' == _string_length_validator(min_length=3, max_length=3)(None, 'abc')

    def test_short_string(self):
        with self.assertRaises(ValueError):
            _string_length_validator(min_length=2, max_length=3)(None, 'a')

    def test_long_string(self):
        with self.assertRaises(ValueError):
            _string_length_validator(min_length=2, max_length=3)(None, 'abcd')


class TestSetuptoolsVersionValidator(TestCase):

    def test_valid_version_string(self):
        assert '1.0.0' == _setuptools_version_validator(None, '1.0.0')

    def test_invalid_version_string(self):
        with self.assertRaises(ValueError):
            _setuptools_version_validator(None, '1.0.a')


class TestEmailValidator(TestCase):

    def test_valid_email(self):
        assert 'me@example.com' == _email_validator(None, 'me@example.com')

    def test_valid_email_not_containing_at(self):
        with self.assertRaises(ValueError):
            _email_validator(None, 'me')

    def test_invalid_email(self):
        with self.assertRaises(ValueError):
            _email_validator(None, '[me@example.com]')


class TestCamelCaseValidator(TestCase):

    def test_camel_case(self):
        _camel_case_validator(None, 'HelloWorld')

    def test_snake_case(self):
        with self.assertRaises(ValueError):
            _camel_case_validator(None, 'hello_world')


class TestEscapeSingleQuoteValidator(TestCase):

    def test_escape_single_quote(self):
        assert r"a\\'a" == _escape_single_quote_validator(None, "a'a")


class TestGenericAddonWizard(TestCase):

    def setUp(self):
        self.system_stdin = sys.stdin

    def tearDown(self):
        sys.stdin = self.system_stdin

    def test_wizard_returns_none_if_aborted(self):
        sys.stdin = StringIO('quit\n')
        assert run_generic_addon_wizard() is None

    def test_successfully_running_the_wizard(self):
        sys.stdin = StringIO(
            (
                'framework\n'
                'addon_name\n'
                '1.2.3\n'
                'this is my description\n'
                'this is my long description\n'
                'maintainer\n'
                'maintainer@somewhere.com\n'
                'zflash==1.2.3\n'
                'MyEntryPoint\n'
                '.\n'))

        data = run_generic_addon_wizard()
        assert data.addon_type == 'framework'
        assert data.package_name == 'addon_name'
        assert data.version == '1.2.3'
        assert data.description == 'this is my description'
        assert data.long_description == 'this is my long description'
        assert data.maintainer == 'maintainer'
        assert data.maintainer_email == 'maintainer@somewhere.com'
        assert data.install_requires == 'zflash==1.2.3'
        assert data.entrypoint == 'MyEntryPoint'
        assert data.addon_path == '.'
