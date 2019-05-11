"""Tests the config module."""

import unittest

from ..config import AttributeErrorContext, AttributeErrorInfo, ParseMarkerErrorInfo, \
    RawConfigParser, dict_to_raw_config
from .utils.parameterized import parameterized


class TestDictToConfig(unittest.TestCase):

    def test_dict_to_config_simple_object(self):
        config = dict_to_raw_config({'attr': 'value'})
        self.assertEqual('value', config.attr)

    def test_dict_nested_object(self):
        config = dict_to_raw_config({'attr': {'subattr': 'value'}})
        self.assertEqual('value', config.attr.subattr)

    def test_list_of_objects(self):
        obj = {'attr': 'value'}
        config = dict_to_raw_config([obj, obj])
        self.assertEqual(2, len(config))
        self.assertEqual('value', config[0].attr)


class TestRawConfigParser(unittest.TestCase):

    @parameterized.expand(['a', 'a(.*)', '[A-Z]+'])
    def test_parse_valid_raw_markers(self, raw_marker):
        """Test that a valid marker is a string that can be compiled into a regular expression."""
        self.assertEqual(
            'SRE_Pattern',
            type(RawConfigParser().parse_raw_marker(raw_marker)).__name__)

    @parameterized.expand([('(,*')])
    def test_parse_invalid_raw_markers_raises_error(self, raw_markers):
        with self.assertRaises(ParseMarkerErrorInfo):
            RawConfigParser().parse_raw_marker(raw_markers)

    @parameterized.expand(
        [
            (str, '', True), (str, 10, False), (str, [], False), (list, [], True),
            (list, '', False), ('invalid_type', 'foo', False)
        ])
    def test_check_config_type(self, value_type, config_obj, expected):
        result = RawConfigParser().check_config_value_type(value_type, config_obj)
        self.assertEqual(expected, result)

    def test_parse_markers_collects_errors(self):
        raw_invalid_markers = ['(,*', '(,*']
        parser = RawConfigParser()
        parser.parse_raw_markers(raw_invalid_markers, [])
        errors = parser.get_errors()
        self.assertEqual(1, len(errors))

    def test_clear_errors(self):
        parser = RawConfigParser()
        parser.add_error(1, None)
        self.assertEqual(1, len(parser.get_errors()), 'Precondition not meat. Expected 1 error.')
        parser.clear_errors()
        self.assertEqual(0, len(parser.get_errors()), 'Error was not been cleared')

    def test_parse_raw_definition_complete_object(self):
        parser = RawConfigParser()
        raw_definition = dict_to_raw_config(
            {
                'title': 'TITLE',
                'id': 'ID',
                'desc': 'DESCRIPTION',
                'markers': [],
                'watchers': []
            })
        definition = parser.parse_raw_definition(raw_definition)
        self.assertIsNotNone(definition)
        self.assertEqual(0, len(parser.get_errors()), 'Unexpected errors found')

    def test_parse_raw_definition_invalid_attr_results_in_errors_and_none_defintion(self):
        parser = RawConfigParser()
        raw_definition = dict_to_raw_config(
            {
                'title': 'TITLE',
                'id': 'ID',
                'desc': 'DESCRIPTION',
                'markers': [],
                'invalid_attr1': 'value',
                'invalid_attr2': 'value'
            })
        definition = parser.parse_raw_definition(raw_definition)
        self.assertEqual(1, len(parser.get_errors()))
        self.assertIsNone(definition)

    def test_one_error_per_id(self):
        parser = RawConfigParser()
        err_id = 'id'
        parser.add_error(err_id, None)
        parser.add_error(err_id, None)
        errors = parser.get_errors()
        self.assertEqual(1, len(errors), 'Expected only one error in error-list')

    def test_parse_raw_root_with_empty_definition_list(self):
        raw_config = dict_to_raw_config({'definitions': []})
        parser = RawConfigParser()
        config = parser.parse_raw_root(raw_config)
        self.assertEqual([], config.definitions, 'definitions was not empty list as expected')

    def test_duplicated_id_result_in_error(self):
        raw_config = dict_to_raw_config(
            {
                'definitions': [
                    {
                        'markers': ['a'],
                        'title': 'Title1',
                        'id': 'ID1',
                        'desc': 'Description1'
                    }, {
                        'markers': ['b'],
                        'title': 'Title2',
                        'id': 'ID1',
                        'desc': 'Description2'
                    }
                ]
            })
        parser = RawConfigParser()
        parser.parse_raw_root(raw_config)
        errors = parser.get_errors()
        self.assertEqual(1, len(errors), 'Expected only one error in error-list')

    def test_multiple_duplicated_ids_result_in_multiple_errors(self):
        raw_config = dict_to_raw_config(
            {
                'definitions': [
                    {
                        'markers': ['a'],
                        'title': 'Title1',
                        'id': 'ID1',
                        'desc': 'Description1'
                    }, {
                        'markers': ['b'],
                        'title': 'Title2',
                        'id': 'ID1',
                        'desc': 'Description2'
                    }, {
                        'markers': ['c'],
                        'title': 'Title3',
                        'id': 'ID1',
                        'desc': 'Description3'
                    }
                ]
            })
        parser = RawConfigParser()
        parser.parse_raw_root(raw_config)
        errors = parser.get_errors()
        self.assertEqual(2, len(errors), 'Expected two errors in error-list')

    def test_parse_raw_config(self):
        raw_config = dict_to_raw_config(
            {
                'definitions': [
                    {
                        'markers': ['a'],
                        'title': 'Title1',
                        'id': 'ID1',
                        'desc': 'Description1',
                        'watchers': ['email@example.com']
                    }, {
                        'markers': ['b'],
                        'title': 'Title2',
                        'id': 'ID2',
                        'desc': 'Description2'
                    }
                ]
            })
        config = RawConfigParser().parse_raw_root(raw_config)
        self.assertEqual('Title1', config.definitions[0].title)
        self.assertEqual('Title2', config.definitions[1].title)

    def test_parse_raw_markers_with_config_check_on_gives_error_if_markers_not_covered_by_samples(
            self):
        raw_marker = '.*'
        raw_markers = dict_to_raw_config([raw_marker])
        samples = []
        parser = RawConfigParser(True)
        parser.parse_raw_markers(raw_markers, samples)
        errors = parser.get_errors()
        self.assertEqual(1, len(errors))
        self.assertEqual("Missing sample for: '.*'\n\n", str(errors[raw_marker]))

    def test_parse_raw_emails_with_invalid_email_address(self):
        email = 'invalid email'
        emails = [email]
        parser = RawConfigParser(True)
        parser.parse_raw_emails(emails)
        errors = parser.get_errors()
        self.assertEqual(1, len(errors))
        self.assertEqual("Invalid email address: 'invalid email'\n\n", str(errors[email]))


class TestAttributeErrors(unittest.TestCase):

    def test_attribute_error_context_to_str(self):
        cxt = AttributeErrorContext('attr', 'error')
        self.assertEqual("error: 'attr'\n", str(cxt))

    def test_attribute_error_info_to_str_max_line_limit(self):
        dict_cfg = {}
        for i in range(1, 5):
            dict_cfg['attr' + str(i)] = 'value' + str(i)
        raw_config = dict_to_raw_config(dict_cfg)
        info = AttributeErrorInfo('type', raw_config)
        info.max_lines = 1
        expected = """type:
'attr1: value1
...'
"""
        self.assertEqual(expected, str(info))
