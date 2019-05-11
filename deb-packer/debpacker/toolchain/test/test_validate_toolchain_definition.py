from unittest import TestCase

from voluptuous import MultipleInvalid

from debpacker.toolchain.configuration import ToolchainLink, _validate_toolchain_definition


class TestValidateToolchainDefinition(TestCase):

    def setUp(self):
        self.data = {
            'name': 'zenterio-name1',
            'version': '1.0.0',
            'url': 'https://test.zenterio.lan/file',
            'paths': ['/first/abs/path', 'second/relative/path'],
        }
        self.expected_links = self.data.copy()
        self.expected_links['toolchain_root'] = ''
        self.expected_links['links'] = []
        self.expected_links['depends'] = []

    def test_valid_data(self):
        validated_data = _validate_toolchain_definition(self.data)
        self.assertEqual(self.expected_links, validated_data)

    def test_missing_keys(self):
        del self.data['paths']
        with self.assertRaises(MultipleInvalid):
            _validate_toolchain_definition(self.data)

    def test_remove_extra(self):
        self.data['extra'] = 'extra_value'
        validated_data = _validate_toolchain_definition(self.data)
        self.assertEqual(self.expected_links, validated_data)

    def test_empty_paths_list(self):
        self.data['paths'].clear()
        with self.assertRaises(MultipleInvalid):
            _validate_toolchain_definition(self.data)

    def test_convert_single_path_to_list(self):
        self.data['paths'] = 'path'
        validated_data = _validate_toolchain_definition(self.data)
        self.assertEqual(validated_data['paths'], ['path'])

    def test_optional_toolchain_root(self):
        self.data['toolchain_root'] = 'some/path'
        self.expected_links['toolchain_root'] = 'some/path'
        validated_data = _validate_toolchain_definition(self.data)
        self.assertEqual(validated_data, self.expected_links)

    def test_that_string_link_raises_exception(self):
        self.data['links'] = 'some/path'
        with self.assertRaises(MultipleInvalid):
            _validate_toolchain_definition(self.data)

    def test_that_link_list_will_raises_exception(self):
        self.data['links'] = ['some/path']
        with self.assertRaises(MultipleInvalid):
            _validate_toolchain_definition(self.data)

    def test_correct_format_of_links(self):
        self.data['links'] = {'some/path': 'some/dst/path', 'more/src/path': 'last/dst/path'}
        self.expected_links = {
            ToolchainLink('some/path', 'some/dst/path'),
            ToolchainLink('more/src/path', 'last/dst/path')
        }
        validated_data = _validate_toolchain_definition(self.data)
        self.assertEqual(self.expected_links, set(validated_data['links']))
