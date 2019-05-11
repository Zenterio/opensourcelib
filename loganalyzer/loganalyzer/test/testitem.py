"""
Tests the classes in the multiconfigreader module.

Note: uses relative imports and hence the parent module need to be loaded.
"""
import re
import unittest

from ..item import ItemDefinition, ItemInstance, LogData, LogMatch
from .utils.parameterized import parameterized


class TestItemDefinition(unittest.TestCase):

    def test_each_definition_has_unique_id(self):
        itemdef1 = ItemDefinition(None, None)
        itemdef2 = ItemDefinition(None, None)
        self.assertNotEqual(
            itemdef1.definition_id, itemdef2.definition_id, 'Expected definition id to be unique')


class TestItemInstance(unittest.TestCase):

    def test_complete(self):
        instance = ItemInstance(ItemDefinition(['a', 'b'], []))
        self.assertFalse(
            instance.is_complete(), 'Instance with no matches expected not to be complete but was.')
        instance.set_match(1, LogMatch(None, None))
        self.assertFalse(
            instance.is_complete(), 'Incomplete instance expected not to be complete but was.')
        instance.set_match(0, LogMatch(None, None))
        self.assertTrue(
            instance.is_complete(),
            'Instance with all matches expected to be complete but was not.')

    def test_invalid(self):
        instance = ItemInstance(ItemDefinition(['a'], ['b', 'c']))
        self.assertFalse(
            instance.is_invalid(),
            'instance with no invalidators expected not to be invalid bud was.')
        instance.set_invalid(0, LogMatch(None, None))
        self.assertFalse(
            instance.is_invalid(),
            'instance with incomplete invalidators expected not to be invalid bud was.')
        instance.set_invalid(1, LogMatch(None, None))
        self.assertTrue(
            instance.is_invalid(), 'instance with all invalidators expected to be invalid bud was.')


class TestLogMatch(unittest.TestCase):

    def test_str(self):
        matcher = LogMatch(LogData(1, 'content'), None)
        self.assertEqual('1:content', str(matcher))

    equal = [
        (
            LogMatch(LogData(1, 'content'), re.search('a', 'a')),
            LogMatch(LogData(1, 'content'), re.search('a', 'a'))),
        (LogMatch(LogData(1, 'content'), None), LogMatch(LogData(1, 'content'), None)),
        (LogMatch(None, None), LogMatch(None, None)),
    ]

    not_equal = [
        (
            LogMatch(LogData(1, 'content'), re.search('a', 'a')),
            LogMatch(LogData(1, 'content'), re.search('b', 'b'))),
        (
            LogMatch(LogData(1, 'content'), re.search('a', 'a')),
            LogMatch(LogData(1, 'content'), None)),
        (
            LogMatch(LogData(1, 'content'), None),
            LogMatch(LogData(1, 'content'), re.search('b', 'b'))),
        (LogMatch(LogData(1, 'content'), None), LogMatch(LogData(2, 'other'), None)),
        (LogMatch(None, None), LogMatch(LogData(2, 'content'), None)),
    ]

    @parameterized.expand(equal)
    def test_eq(self, m1, m2):
        self.assertEqual(m1, m2, 'Expected equality, but was not.')

    @parameterized.expand(not_equal)
    def test_ne(self, m1, m2):
        self.assertNotEqual(m1, m2, 'Expected non-equality, but was.')


class TestLogData(unittest.TestCase):

    def test_str(self):
        data = LogData(1, 'content')
        self.assertEqual('1:content', str(data))

    equal = [
        (LogData(None, None), LogData(None, None)), (LogData(1, 'content'), LogData(1, 'content'))
    ]

    not_equal = [
        (LogData(1, None), LogData(2, None)), (LogData(None, 'content'), LogData(None, 'other'))
    ]

    @parameterized.expand(equal)
    def test_eq(self, m1, m2):
        self.assertEqual(m1, m2, 'Expected equality, but was not.')

    @parameterized.expand(not_equal)
    def test_ne(self, d1, d2):
        self.assertNotEqual(d1, d2, 'Expected non-equality, but was.')
