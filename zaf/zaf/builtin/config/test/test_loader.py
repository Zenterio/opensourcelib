import unittest

from ..loader import ADDITIONAL_CONFIG_GLOB_PATTERN, CONFIG_GLOB_PATTERN, \
    DISABLE_DEFAULT_CONFIG_FILES, LOCAL_CONFIG_GLOB_PATTERN, LOCAL_CONFIG_GLOB_PATTERN_ENABLED, \
    SYSTEM_CONFIG_GLOB_PATTERN, SYSTEM_CONFIG_GLOB_PATTERN_ENABLED, USER_CONFIG_GLOB_PATTERN, \
    USER_CONFIG_GLOB_PATTERN_ENABLED, AdditionalFileConfigLoader, ConfigLoaderError, \
    DisableDefaultConfigFileLoader, ExplicitFileConfigLoader, LocalFileConfigLoader, \
    SystemFileConfigLoader, UserFileConfigLoader, _validate_configuration


class TestExplicitFileConfigLoader(unittest.TestCase):

    def test_enabled(self):
        loader = ExplicitFileConfigLoader({CONFIG_GLOB_PATTERN: ['a', 'b', 'c']}, None)
        self.assertEqual(loader.config_file_glob_patterns, ['a', 'b', 'c'])

    def test_priority(self):
        loader = ExplicitFileConfigLoader({}, None)
        self.assertEqual(loader.priority, 50)


class TestSystemFileConfigLoader(unittest.TestCase):

    def test_enabled(self):
        loader = SystemFileConfigLoader(
            {
                SYSTEM_CONFIG_GLOB_PATTERN_ENABLED: True,
                SYSTEM_CONFIG_GLOB_PATTERN: '/etc/zaf/config'
            }, None)
        self.assertEqual(loader.config_file_glob_patterns, ['/etc/zaf/config'])

    def test_disabled(self):
        loader = SystemFileConfigLoader(
            {
                SYSTEM_CONFIG_GLOB_PATTERN_ENABLED: False,
                SYSTEM_CONFIG_GLOB_PATTERN: '/etc/zaf/config'
            }, None)
        self.assertEqual(loader.config_file_glob_patterns, [])

    def test_priority(self):
        loader = SystemFileConfigLoader({}, None)
        self.assertEqual(loader.priority, 10)


class TestUserFileConfigLoader(unittest.TestCase):

    def test_enabled(self):
        loader = UserFileConfigLoader(
            {
                USER_CONFIG_GLOB_PATTERN_ENABLED: True,
                USER_CONFIG_GLOB_PATTERN: '~/.zafconfig'
            }, None)
        self.assertEqual(loader.config_file_glob_patterns, ['~/.zafconfig'])

    def test_disabled(self):
        loader = UserFileConfigLoader(
            {
                USER_CONFIG_GLOB_PATTERN_ENABLED: False,
                USER_CONFIG_GLOB_PATTERN: '~/.zafconfig'
            }, None)
        self.assertEqual(loader.config_file_glob_patterns, [])

    def test_priority(self):
        loader = UserFileConfigLoader({}, None)
        self.assertEqual(loader.priority, 20)


class TestLocalFileConfigLoader(unittest.TestCase):

    def test_enabled(self):
        loader = LocalFileConfigLoader(
            {
                LOCAL_CONFIG_GLOB_PATTERN_ENABLED: True,
                LOCAL_CONFIG_GLOB_PATTERN: './zafconfig'
            }, None)
        self.assertEqual(loader.config_file_glob_patterns, ['./zafconfig'])

    def test_disabled(self):
        loader = LocalFileConfigLoader(
            {
                LOCAL_CONFIG_GLOB_PATTERN_ENABLED: False,
                LOCAL_CONFIG_GLOB_PATTERN: './zafconfig'
            }, None)
        self.assertEqual(loader.config_file_glob_patterns, [])

    def test_priority(self):
        loader = LocalFileConfigLoader({}, None)
        self.assertEqual(loader.priority, 30)


class TestAdditionalFileConfigLoader(unittest.TestCase):

    def test_enabled(self):
        loader = AdditionalFileConfigLoader({ADDITIONAL_CONFIG_GLOB_PATTERN: ['a', 'b', 'c']}, None)
        self.assertEqual(loader.config_file_glob_patterns, ['a', 'b', 'c'])

    def test_priority(self):
        loader = AdditionalFileConfigLoader({}, None)
        self.assertEqual(loader.priority, 40)


class TestValidateConfiguration(unittest.TestCase):

    def test_empty_dict(self):
        _validate_configuration({})

    def test_int_value(self):
        _validate_configuration({'str': 123})

    def test_bool_value(self):
        _validate_configuration({'str': True})

    def test_str_value(self):
        _validate_configuration({'str': 'str'})

    def test_list_value(self):
        _validate_configuration({'str': [1, 2, 3]})

    def test_dict_value(self):
        with self.assertRaises(ConfigLoaderError):
            _validate_configuration({'str': {1: 2}})

    def test_object_value(self):
        with self.assertRaises(ConfigLoaderError):
            _validate_configuration({'str': object()})

    def test_non_str_key(self):
        with self.assertRaises(ConfigLoaderError):
            _validate_configuration({123: 'str'})

    def test_list_value_containing_int(self):
        _validate_configuration({'str': [1]})

    def test_list_value_containing_bool(self):
        _validate_configuration({'str': [True]})

    def test_list_value_containing_str(self):
        _validate_configuration({'str': ['str']})

    def test_list_value_containing_empty_dict(self):
        with self.assertRaises(ConfigLoaderError):
            _validate_configuration({'str': [{}]})

    def test_list_value_containing_non_empty_dict(self):
        with self.assertRaises(ConfigLoaderError):
            _validate_configuration({'str': [{1: 2}]})


class TestDisableDefaultConfigFileLoader(unittest.TestCase):

    def test_enabled(self):
        loader = DisableDefaultConfigFileLoader({DISABLE_DEFAULT_CONFIG_FILES: True})

        self.assertFalse(loader.default_config[SYSTEM_CONFIG_GLOB_PATTERN_ENABLED.name])
        self.assertFalse(loader.default_config[LOCAL_CONFIG_GLOB_PATTERN_ENABLED.name])
        self.assertFalse(loader.default_config[USER_CONFIG_GLOB_PATTERN_ENABLED.name])

    def test_priority(self):
        loader = DisableDefaultConfigFileLoader({DISABLE_DEFAULT_CONFIG_FILES: True})
        self.assertEqual(loader.priority, 50)
