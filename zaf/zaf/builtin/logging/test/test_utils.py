import unittest

from zaf.builtin.logging.utils import combine_loggers


class TestCombineLoggers(unittest.TestCase):

    def test_all_loggers_combine_with_root_logger(self):
        self.assertEqual(combine_loggers(['', 'a']), [''])
        self.assertEqual(combine_loggers(['', 'a', 'a.b', 'b', 'b.d.e']), [''])
        self.assertEqual(combine_loggers(['a', 'a.b', 'b', '', 'b.d.e']), [''])

    def test_child_logger_combine_into_parent_logger(self):
        self.assertEqual(combine_loggers(['a', 'a.b']), ['a'])
        self.assertEqual(combine_loggers(['a.b.c', 'a.b']), ['a.b'])

    def test_sibling_loggers_are_kept(self):
        self.assertEqual(combine_loggers(['a.b', 'a.c']), ['a.b', 'a.c'])
        self.assertEqual(combine_loggers(['a.c', 'a.b']), ['a.c', 'a.b'])
        self.assertEqual(combine_loggers(['a', 'b']), ['a', 'b'])
