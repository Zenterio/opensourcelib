from io import StringIO
from textwrap import dedent
from unittest import TestCase
from unittest.mock import mock_open, patch

from ..data import DataDefinition
from ..writers import AbstractFileWriter, CsvWriter, JsonWriter, SingleValueTextWriter


class TestDataDefinition(DataDefinition):

    def __init__(self, default=None):
        super().__init__(['a', 'bb', 'ccc'], default)


class TestAbstractFileWriter(TestCase):

    class MyWriter(AbstractFileWriter):

        def write_to_stream(self, data, stream):
            self.stream = stream

    def test_directories_are_created_if_needed(self):
        with patch('os.makedirs') as mock_makedirs,\
             patch('builtins.open', new_callable=mock_open) as mocked_open:
            TestAbstractFileWriter.MyWriter('path/to/report').write(None)
            mock_makedirs.assert_called_once_with('path/to', exist_ok=True)
            mocked_open.assert_called_once_with('path/to/report', 'w')

    def test_path_dash_means_stdout(self):
        with patch('sys.stdout') as mock_stdout:
            writer = TestAbstractFileWriter.MyWriter('-')
            writer.write(None)
            self.assertEqual(mock_stdout, writer.stream)


class TestJsonWriter(TestCase):

    def test_write_with_no_data(self):
        path = 'path/to/report.json'
        writer = JsonWriter(path)
        data = TestDataDefinition()
        stream = StringIO()
        writer.write_to_stream(data, stream)
        expected = dedent(
            """\
        {
            "a": null,
            "bb": null,
            "ccc": null
        }""")
        self.assertEqual(stream.getvalue(), expected)

    def test_write_with_data(self):
        path = 'path/to/report.json'
        writer = JsonWriter(path)
        data = TestDataDefinition()
        data.a = 1
        data.bb = 'my_string'
        data.ccc = ['item1', 'item2']
        stream = StringIO()
        writer.write_to_stream(data, stream)
        expected = dedent(
            """\
        {
            "a": 1,
            "bb": "my_string",
            "ccc": [
                "item1",
                "item2"
            ]
        }""")
        self.assertEqual(stream.getvalue(), expected)


class TestCsvWriter(TestCase):

    def test_write_with_no_data(self):
        writer = CsvWriter(None)
        data = TestDataDefinition()
        stream = StringIO()
        writer.write_to_stream(data, stream)
        expected = 'a,bb,ccc\r\n,,\r\n'
        self.assertEqual(stream.getvalue(), expected)

    def test_write_with_data(self):
        writer = CsvWriter(None)
        data = TestDataDefinition()
        data.a = 1
        data.bb = 2
        data.ccc = 3
        stream = StringIO()
        writer.write_to_stream(data, stream)
        expected = 'a,bb,ccc\r\n1,2,3\r\n'
        self.assertEqual(stream.getvalue(), expected)


class TestSingleValueTextWriter(TestCase):

    def test_write_with_no_data(self):
        writer = SingleValueTextWriter(None)
        data = TestDataDefinition()
        stream = StringIO()
        writer.write_to_stream(data, stream)
        expected = 'a  : \nbb : \nccc: \n'
        self.assertEqual(stream.getvalue(), expected)

    def test_write_with_data(self):
        writer = SingleValueTextWriter(None)
        data = TestDataDefinition()
        data.a = 1
        data.bb = 2
        data.ccc = 3
        stream = StringIO()
        writer.write_to_stream(data, stream)
        expected = 'a  : 1\nbb : 2\nccc: 3\n'
        self.assertEqual(stream.getvalue(), expected)
