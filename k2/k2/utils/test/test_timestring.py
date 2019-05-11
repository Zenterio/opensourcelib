import unittest

from zaf.config import ConfigException

from k2.utils.timestring import parse_time


class TestParseTimeString(unittest.TestCase):

    def testparse_time_throws_exception_if_invalid_input(self):
        too_many_numbers = '4:3:2:1'
        invalid_seperator = '5;2'
        not_a_number = 'test'
        with self.assertRaises(ConfigException):
            parse_time(too_many_numbers)
        with self.assertRaises(ConfigException):
            parse_time(invalid_seperator)
        with self.assertRaises(ConfigException):
            parse_time(not_a_number)

    def testparse_time_parses_time(self):
        only_seconds = '522'
        only_minutes = '15:0'
        only_hours = '1:0:0'
        seconds_and_minutes = '3:15'
        hours_and_minutes = '1:2:0'
        all_three = '3:2:1'
        more_than_60_seconds = '3:80'
        more_than_60_minutes = '100:0'

        self.assertEqual(parse_time(only_seconds), 522)
        self.assertEqual(parse_time(only_minutes), 900)
        self.assertEqual(parse_time(only_hours), 3600)
        self.assertEqual(parse_time(seconds_and_minutes), 195)
        self.assertEqual(parse_time(hours_and_minutes), 3720)
        self.assertEqual(parse_time(all_three), 10921)
        self.assertEqual(parse_time(more_than_60_seconds), 260)
        self.assertEqual(parse_time(more_than_60_minutes), 6000)

    def testparse_time_falsy_time_string_returns_none(self):
        self.assertIsNone(parse_time(''), None)
        self.assertIsNone(parse_time(None), None)
