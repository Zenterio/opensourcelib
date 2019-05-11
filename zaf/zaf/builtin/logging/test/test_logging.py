import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from zaf.application import APPLICATION_NAME
from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.extensions import ENABLED_EXTENSIONS
from zaf.extensions.extension import get_logger_name

from .. import EXTENSION_LOG_LEVEL, LOG_DEBUG, LOG_DIR, LOG_ERROR, LOG_FORMAT, LOG_INFO, \
    LOG_LEVEL, LOG_WARNING
from ..logging import RootLogger, map_level


class RootLoggerTest(unittest.TestCase):

    def test_sets_root_logger_level_and_attaches_stdout_handler(self):
        logger = MagicMock()
        handler = Mock()

        config = ConfigManager()
        config.set(LOG_LEVEL, 'warning')

        with patch('logging.getLogger', return_value=logger), \
                patch('logging.StreamHandler', return_value=handler), \
                patch('zaf.builtin.logging.logging.Filter', return_value=filter) as get_filter:
            with ExtensionTestHarness(RootLogger, config=config):
                logger.setLevel.assert_called_with(logging.DEBUG)
                logger.addHandler.assert_called_with(handler)
                self.assertEqual(handler.addFilter.call_count, 1)
                get_filter.assert_called_with({'': 30})

    def test_sets_format_string_to_config_value(self):
        logger = MagicMock()
        handler = Mock()
        formatter = Mock()

        config = ConfigManager()
        config.set(LOG_FORMAT, 'hej')

        with patch('logging.getLogger', return_value=logger), \
                patch('logging.StreamHandler', return_value=handler), \
                patch('zaf.builtin.logging.logging.Filter', return_value=filter) as get_filter, \
                patch('logging.Formatter', return_value=formatter) as formatter_constructor:

            with ExtensionTestHarness(RootLogger, config=config):
                formatter_constructor.assert_called_with('hej')
                handler.setFormatter.assert_called_with(formatter)
                get_filter.assert_called_with({'': 20})

    def test_can_set_level_for_specific_loggers(self):
        logger = MagicMock()

        config = ConfigManager()
        config.set(LOG_DEBUG, ['test1'])
        config.set(LOG_INFO, ['test2'])
        config.set(LOG_WARNING, ['test3'])
        config.set(LOG_ERROR, ['test4'])

        with patch('logging.getLogger', return_value=logger), \
                patch('zaf.builtin.logging.logging.Filter', return_value=filter) as get_filter:
            with ExtensionTestHarness(RootLogger, config=config):
                get_filter.assert_called_with(
                    {
                        '': 20,
                        'test1': 10,
                        'test2': 20,
                        'test3': 30,
                        'test4': 40
                    })

    def test_sets_extension_logger_level(self):
        logger = Mock()
        filter = Mock()

        config = ConfigManager()
        config.set(APPLICATION_NAME, 'k2')
        config.set(ENABLED_EXTENSIONS, ['extensionname'])
        config.set(EXTENSION_LOG_LEVEL, 'error', entity='extensionname')

        with patch('logging.getLogger', return_value=logger) as get_logger,  \
                patch('zaf.builtin.logging.logging.Filter', return_value=filter) as get_filter:
            with ExtensionTestHarness(RootLogger, config=config):
                get_logger.assert_any_call(get_logger_name('zaf', 'extensionname'))
                get_logger.assert_any_call(get_logger_name('k2', 'extensionname'))
                logger.setLevel.assert_called_with(logging.DEBUG)
                get_filter.assert_called_with(
                    {
                        '': 20,
                        'k2.extension.extensionname': 40,
                        'zaf.extension.extensionname': 40
                    })

    def test_does_not_set_extension_logger_level_if_none(self):
        logger = Mock()

        config = ConfigManager()
        config.set(LOG_LEVEL, 'warning')
        config.set(LOG_FORMAT, 'hej')
        config.set(LOG_DIR, '.')
        config.set(APPLICATION_NAME, 'k2')
        config.set(ENABLED_EXTENSIONS, ['extensionname'])
        config.set(EXTENSION_LOG_LEVEL, None, entity='extensionname')

        with patch('logging.getLogger', return_value=logger) as get_logger, \
                patch('zaf.builtin.logging.logging.Filter', return_value=filter) as get_filter:
            with ExtensionTestHarness(RootLogger, config=config):
                get_logger.assert_any_call(get_logger_name('zaf', 'extensionname'))
                get_logger.assert_any_call(get_logger_name('k2', 'extensionname'))
                logger.setLevel.assert_called_with(logging.DEBUG)
                get_filter.assert_called_with({'': 30})


class LevelMapping(unittest.TestCase):

    def test_that_levels_are_mapped_from_string_to_logging(self):
        self.assertEqual(map_level('debug'), logging.DEBUG)
        self.assertEqual(map_level('DEBUG'), logging.DEBUG)
        self.assertEqual(map_level('info'), logging.INFO)
        self.assertEqual(map_level('INFO'), logging.INFO)
        self.assertEqual(map_level('warning'), logging.WARNING)
        self.assertEqual(map_level('WARNING'), logging.WARNING)
        self.assertEqual(map_level('error'), logging.ERROR)
        self.assertEqual(map_level('ERROR'), logging.ERROR)
        self.assertIsNone(map_level(None))
        self.assertIsNone(map_level('NOT SUPPORTED VALUE'), None)
