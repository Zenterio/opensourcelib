import logging
import unittest
from unittest.mock import Mock, call, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from .. import ENTER_LOG_SCOPE, EXIT_LOG_SCOPE, LOG_DIR, LOG_END_POINT, LOG_FILE_ENABLED, \
    LOG_FILE_LEVEL, LOG_FILE_LOGGERS, LOG_FILE_PATH, LOG_FILE_ROTATE_DELETE_RESULTS, \
    LOG_FILE_ROTATE_SCOPE, LOG_FILES, LogScopeMessageData
from ..file import FileLogger


class FileLoggerTest(unittest.TestCase):

    def setUp(self):
        self.handler = mock_handler()

    def test_set_up_file_handler_without_rotate(self):
        with FileLoggerHarness(self.handler, config=default_config()) as harness:
            harness.handler_constructor.assert_called_with('path', 'w', delay=True)
            harness.getlogger.assert_has_calls([call('logger1'), call('logger2')], any_order=True)
            self.assertFalse(
                harness.harness.any_registered_dispatchers(ENTER_LOG_SCOPE, LOG_END_POINT))
            for logger in harness.loggers.values():
                logger.addHandler.assert_called_with(self.handler)


class RotatingFileLoggerTest(unittest.TestCase):

    def setUp(self):
        self.handler = mock_handler()
        self.config = default_config()
        self.config.set(LOG_FILE_ROTATE_SCOPE, 'testcase', entity='file')

    def test_set_up_rotating_file_handler(self):
        with FileLoggerHarness(self.handler, self.config, handler_type='scope') as harness:
            harness.handler_constructor.assert_called_with('path', 'testcase')

            for logger in harness.loggers.values():
                logger.addHandler.assert_called_with(self.handler)

            self.handler.setLevel.assert_called_with(100)
            self.assertTrue(
                harness.harness.any_registered_dispatchers(ENTER_LOG_SCOPE, LOG_END_POINT))
            self.assertTrue(
                harness.harness.any_registered_dispatchers(EXIT_LOG_SCOPE, LOG_END_POINT))

    def test_log_rotation_is_performed_when_receiving_messages(self):
        with FileLoggerHarness(self.handler, self.config, handler_type='scope') as harness:
            harness.harness.send_request(
                ENTER_LOG_SCOPE, data=LogScopeMessageData(id='testcase',
                                                          name='name')).wait(timeout=1)
            self.handler.setLevel.assert_called_with(0)

            harness.harness.send_request(
                EXIT_LOG_SCOPE, data=LogScopeMessageData(id='testcase', name='name',
                                                         result='ok')).wait(timeout=1)
            self.handler.exit_scope.assert_called_with('name', False)

    def test_log_rotation_is_not_performed_when_receiving_messages_for_other_scope(self):
        with FileLoggerHarness(self.handler, self.config, handler_type='scope') as harness:
            self.handler.setLevel.reset_mock()

            harness.harness.send_request(
                ENTER_LOG_SCOPE, data=LogScopeMessageData(id='other', name='name')).wait(timeout=1)
            self.handler.setLevel.assert_not_called()

            harness.harness.send_request(
                EXIT_LOG_SCOPE, data=LogScopeMessageData(id='other', name='name',
                                                         result='ok')).wait(timeout=1)
            self.handler.exit_scope.assert_not_called()

    def test_delete_is_called_if_exiting_scope_only_for_deleteforresult_result(self):
        config = default_config()
        config.set(LOG_FILE_ROTATE_SCOPE, 'testcase', entity='file')
        config.set(LOG_FILE_ROTATE_DELETE_RESULTS, ['PASSED'], entity='file')

        with FileLoggerHarness(self.handler, config, handler_type='scope') as harness:
            harness.harness.send_request(
                EXIT_LOG_SCOPE,
                data=LogScopeMessageData(id='testcase', name='name',
                                         result='FAILED')).wait(timeout=1)
            self.handler.exit_scope.assert_called_with('name', False)

            self.handler.reset_mock()
            harness.harness.send_request(
                EXIT_LOG_SCOPE,
                data=LogScopeMessageData(id='testcase', name='name',
                                         result='PASSED')).wait(timeout=1)
            self.handler.exit_scope.assert_called_with('name', True)


class FileLoggerHarness(object):

    def __init__(self, handler_mock, config=None, handler_type='file'):
        self.loggers = {}

        def get_logger(name):
            if name not in self.loggers:
                self.loggers[name] = mock_logger()

            return self.loggers[name]

        self.getlogger_patch = patch('logging.getLogger', side_effect=get_logger)
        if handler_type == 'file':
            self.handler_qual_name = 'logging.FileHandler'
        else:
            self.handler_qual_name = 'zaf.builtin.logging.file.ScopedRotatingLogHandler'

        self.handler_constructor_patch = patch(self.handler_qual_name, return_value=handler_mock)

        self.harness = ExtensionTestHarness(FileLogger, config=config)

    def __enter__(self):
        self.getlogger = self.getlogger_patch.__enter__()
        self.handler_constructor = self.handler_constructor_patch.__enter__()
        self.harness.__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.getlogger_patch.__exit__()
        self.handler_constructor_patch.__exit__()
        self.harness.__exit__()


def mock_logger(level=logging.INFO):
    logger = Mock()
    logger.getEffectiveLevel.return_value = level
    return logger


def mock_handler():
    return Mock()


def default_config():
    config = ConfigManager()
    config.set(LOG_FILES, ['file'])
    config.set(LOG_FILE_ENABLED, True, entity='file')
    config.set(LOG_FILE_PATH, 'path', entity='file')
    config.set(LOG_FILE_LOGGERS, ['logger1', 'logger2'], entity='file')
    config.set(LOG_FILE_LEVEL, 'debug', entity='file')
    config.set(LOG_DIR, '')

    return config
