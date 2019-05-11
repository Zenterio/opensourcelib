"""
Tests the classes in the datasources module.

Note: uses relative imports and hence the parent module need to be loaded.
"""
import unittest
from io import StringIO

from loganalyzer.datasources import StreamDataSource

from ..item import LogData


class TestApplication(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.stream = StringIO('\n'.join(['one', 'two', 'three']))
        self.datasource = StreamDataSource(self.stream)

    def test_read_all_data_in_stream(self):
        all_data = list(self.datasource.get_data())
        expected_data = [LogData(1, 'one'), LogData(2, 'two'), LogData(3, 'three')]
        self.assertEqual(expected_data, all_data, 'The captured data was not what was expected.')
