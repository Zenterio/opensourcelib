import unittest
from io import StringIO
from unittest.mock import Mock, PropertyMock, mock_open, patch

from .. import configreaders
from ..config import ConfigError, ParseMarkerErrorInfo, RawConfigParser, dict_to_raw_config
from ..configreaders import CmdLineConfigReader, EnvVarConfigReader, YAMLConfigReader
from .utils.parameterized import parameterized


class TestYAMLConfigReaderErrors(unittest.TestCase):

    def setUp(self):
        super().setUp()
        mockStream = Mock()
        mockStream.read.side_effect = Exception('Induced error')
        self.reader = YAMLConfigReader(mockStream, False)

    def test_throws_config_error_on_failure_while_parsing(self):
        self.assertRaises(ConfigError, self.reader.get_config)


class TestYAMLConfigReaderParseFromStream(unittest.TestCase):

    def setUp(self):
        super().setUp()
        stream = StringIO(
            """
definitions:
  - title: Title
    id: ID
    desc: Description
    markers:
      - a
      - b
    invalidators:
      - a
      - b
""")
        self.reader = YAMLConfigReader(stream, False)

    def test_get_config_from_stream(self):
        parser = RawConfigParser()
        m1 = parser.parse_raw_marker('a')
        m2 = parser.parse_raw_marker('b')
        config = self.reader.get_config()
        definition = config.definitions[0]
        self.assertEqual('Title', definition.title)
        self.assertEqual('ID', definition.id)
        self.assertEqual('Description', definition.desc)
        self.assertEqual([m1, m2], definition.markers)
        self.assertEqual([m1, m2], definition.invalidators)


class TestYAMLConfigReaderParseMarkerErrors(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.stream = StringIO(
            """
definitions:
  - title: Title
    id: ID
    desc: Description
    markers:
      - invalid reg ex (.* no closing parenthesis
      - b
    invalidators:
      - invalid reg ex (.* no closing parenthesis
      - b
""")
        self.reader = YAMLConfigReader(self.stream, False)
        self.invalid_marker = 'invalid reg ex (.* no closing parenthesis'

    def test_errors_are_collected(self):
        self.assertRaises(Exception, self.reader.get_config)
        errors = self.reader.errors
        self.assertTrue(len(errors), 'Expected at least one error in error-list')

    def test_duplicate_markers_are_captured(self):
        e = ParseMarkerErrorInfo(self.invalid_marker, Exception('Some error'))
        self.reader.errors[self.invalid_marker] = e
        errors = self.reader.identify_errors()
        contexts = errors[self.invalid_marker].contexts
        self.assertEqual(2, len(contexts), 'Expected two contexts')
        self.assertEqual('      - invalid reg ex (.* no closing parenthesis', contexts[0].data)
        self.assertEqual('line 7', contexts[0].index)
        self.assertEqual('      - invalid reg ex (.* no closing parenthesis', contexts[1].data)
        self.assertEqual('line 10', contexts[1].index)

    def test_get_error_msg(self):
        e = ParseMarkerErrorInfo(self.invalid_marker, Exception('Some error'))
        self.reader.errors[self.invalid_marker] = e
        self.reader.identify_errors()
        msg = self.reader.get_error_msg()
        expected = """Configuration parse errors occurred:
Some error: 'invalid reg ex (.* no closing parenthesis'
line 7:      - invalid reg ex (.* no closing parenthesis
line 10:      - invalid reg ex (.* no closing parenthesis
"""
        self.assertEqual(expected, msg)


class TestEnvVarConfigReaderDefaultValues(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.config = EnvVarConfigReader(env={}).get_config()

    def test_profile_is_off_by_default(self):
        self.assertFalse(self.config.profile)

    def test_debug_is_off_by_default(self):
        self.assertFalse(self.config.debug)

    def test_forced_encoding_is_off_by_default(self):
        self.assertIsNone(self.config.encoding)


class TestEnvVarConfigReaderSetValues(unittest.TestCase):

    _r = EnvVarConfigReader

    bool_values = [
        ('n', False), ('no', False), ('False', False), ('F', False), ('0', False), ('', False),
        ('anything-else', True)
    ]

    @parameterized.expand(bool_values)
    def test_parse_bool(self, str_value, exp_value):
        self.assertEqual(exp_value, self._r()._parse_bool(str_value))

    str_values = [('value', 'value'), ('', None), (None, None)]

    @parameterized.expand(str_values)
    def test_parse_str(self, str_value, exp_value):
        self.assertEqual(exp_value, self._r()._parse_str(str_value))

    profile = [(_r.PROFILE, '1', True), (_r.PROFILE, '0', False)]

    @parameterized.expand(profile)
    def test_profile(self, var_name, var_value, cfg_value):
        config = self._r(env={var_name: var_value}).get_config()
        self.assertEqual(cfg_value, config.profile)

    debug = [(_r.DEBUG, '1', True), (_r.DEBUG, '0', False)]

    @parameterized.expand(debug)
    def test_debug(self, var_name, var_value, cfg_value):
        config = self._r(env={var_name: var_value}).get_config()
        self.assertEqual(cfg_value, config.debug)

    encoding = [(_r.ENCODING, 'value', 'value'), (_r.ENCODING, '', None)]

    @parameterized.expand(encoding)
    def test_encoding(self, var_name, var_value, cfg_value):
        config = self._r(env={var_name: var_value}).get_config()
        self.assertEqual(cfg_value, config.encoding)


class TestCmdLineConfigReaderDetectEncoding(unittest.TestCase):

    def call_sut(self, detected_encoding, detected_confidence, preset_encoding):
        with patch(configreaders.__name__ + '.UniversalDetector') as detector, \
                patch('builtins.open', new_callable=mock_open, read_data='data'):
            type(detector.return_value).done = PropertyMock(return_value=True)
            type(detector.return_value).result = PropertyMock(
                return_value={
                    'confidence': detected_confidence,
                    'encoding': detected_encoding
                })
            config = dict_to_raw_config({'encoding': preset_encoding})
            CmdLineConfigReader(None).detect_encoding('path', config)
        return config

    def test_defaults_to_utf8_if_confidence_is_less_than_025_and_no_preset_value(self):
        config = self.call_sut('enc', 0.24, None)
        self.assertEqual('UTF-8', config.encoding)

    def test_detected_encoding_if_confidence_eqgr_025_and_no_preset_value(self):
        config = self.call_sut('enc', 0.25, None)
        self.assertEqual('enc', config.encoding)

    def test_preset_value_has_presidence(self):
        config = self.call_sut('enc', 1, 'preset')
        self.assertEqual('preset', config.encoding)

    def test_records_meta_data_on_config(self):
        config = self.call_sut('enc', 1, None)
        self.assertEqual('enc', config.detected_encoding)
        self.assertEqual(1, config.detected_encoding_confidence)

    def test_no_detection_with_preset_value(self):
        config = self.call_sut('enc', 1, 'preset')
        self.assertEqual(None, config.detected_encoding)
        self.assertEqual(0, config.detected_encoding_confidence)
