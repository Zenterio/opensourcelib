import unittest

from ..extension import get_logger_name


class TestGetLoggerName(unittest.TestCase):

    def test_get_logger_name(self):
        result = get_logger_name('CONTEXT', 'MY_EXTENSION')
        self.assertEqual(result, 'CONTEXT.extension.MY_EXTENSION')

    def test_get_logger_name_with_suffix(self):
        result = get_logger_name('CONTEXT', 'MY_EXTENSION', 'SUF1', 'SUF2')
        self.assertEqual(result, 'CONTEXT.extension.MY_EXTENSION.SUF1.SUF2')
