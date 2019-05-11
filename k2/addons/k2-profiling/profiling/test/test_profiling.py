from unittest import TestCase
from unittest.mock import MagicMock, patch

from zaf.application import AFTER_COMMAND, APPLICATION_ENDPOINT, BEFORE_COMMAND

from ..profiling import Profiling
from .utils import create_harness


def config_mock(
        csv_enabled=False,
        csv_path='path',
        json_enabled=False,
        json_path='path',
        text_enabled=False,
        text_path='path'):
    config = MagicMock()
    config.get.side_effect = [
        csv_enabled, csv_path, json_enabled, json_path, text_enabled, text_path
    ]
    return config


def disabled_config():
    return config_mock(csv_enabled=False, json_enabled=False, text_enabled=False)


def enabled_config():
    return config_mock(csv_enabled=True, json_enabled=True, text_enabled=True)


def csv_config(enabled=True, path='path'):
    return config_mock(csv_enabled=enabled, csv_path=path)


def json_config(enabled=True, path='path'):
    return config_mock(json_enabled=enabled, json_path=path)


def text_config(enabled=True, path='path'):
    return config_mock(text_enabled=enabled, text_path=path)


class TestProfilingAtExit(TestCase):

    def test_on_exit_is_not_registered_atexit_if_disabled(self):
        atexitmock = MagicMock()
        with patch.dict('sys.modules', atexit=atexitmock):
            Profiling(disabled_config(), None)
            self.assertEqual(atexitmock.register.call_count, 0)

    def test_on_exit_is_registered_atexit_if_enabled(self):
        atexitmock = MagicMock()
        with patch.dict('sys.modules', atexit=atexitmock):
            p = Profiling(enabled_config(), None)
            atexitmock.register.assert_called_once_with(p.on_exit)


@patch.dict('sys.modules', atexit=MagicMock())
class TestProfiling(TestCase):

    def test_profiling_always_disabled_for_bash_completion(self):
        with patch('profiling.profiling.is_bash_completion', return_value=True):
            p = Profiling(enabled_config(), None)
            self.assertFalse(p._enabled)

    def test_command_stored_on_before_command(self):
        with create_harness() as harness:
            harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT, data='command_name')
            data = harness.extension._data
            self.assertEqual(data.command, 'command_name')

    def test_start_up_calculation(self):
        with create_harness() as harness:
            harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
            data = harness.extension._data
            self.assertIsNotNone(data.startup_time)
            self.assertIsNotNone(data.startup_process_time)
            self.assertEqual(harness.metrics_mock.call_count, 2)

    def test_command_execution_calculation(self):
        with create_harness() as harness:
            harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
            harness.trigger_event(AFTER_COMMAND, APPLICATION_ENDPOINT)
            data = harness.extension._data
            self.assertIsNotNone(data.command_execution_time)
            self.assertIsNotNone(data.command_execution_process_time)
            self.assertEqual(harness.metrics_mock.call_count, 4)

    def test_k2_execution_calculation(self):
        with create_harness() as harness:
            harness.trigger_event(BEFORE_COMMAND, APPLICATION_ENDPOINT)
            harness.trigger_event(AFTER_COMMAND, APPLICATION_ENDPOINT)
            # disable reporting
            harness.extension._report_csv_enabled = False
            harness.extension._report_json_enabled = False
            harness.extension._report_text_enabled = False
            harness.extension._enabled = False
            # fake on exit event
            harness.extension.on_exit()
            data = harness.extension._data
            self.assertIsNotNone(data.k2_execution_time)
            self.assertIsNotNone(data.k2_execution_process_time)


@patch.dict('sys.modules', atexit=MagicMock())
class TestCsvReporting(TestCase):

    def test_write_reports_writes_csv_report(self):
        p = Profiling(csv_config(), None)
        p.write_csv_report = MagicMock()
        p.write_reports()
        self.assertEqual(p.write_csv_report.call_count, 1)

    def test_write_csv_report_sends_data_to_csvwriter(self):
        path = 'path/to/report.txt'
        data = MagicMock()
        with patch('profiling.profiling.CsvWriter') as CsvWriterMock:
            p = Profiling(csv_config(path=path), None)
            p.write_csv_report(data)
        CsvWriterMock.assert_called_once_with(path)
        CsvWriterMock.return_value.write.assert_called_once_with(data)


@patch.dict('sys.modules', atexit=MagicMock())
class TestJsonReporting(TestCase):

    def test_write_reports_writes_json_report(self):
        p = Profiling(json_config(), None)
        p.write_json_report = MagicMock()
        p.write_reports()
        self.assertEqual(p.write_json_report.call_count, 1)

    def test_write_json_report_sends_data_to_jsonwriter(self):
        path = 'path/to/report.json'
        data = MagicMock()
        with patch('profiling.profiling.JsonWriter') as JsonWriterMock:
            p = Profiling(json_config(path=path), None)
            p.write_json_report(data)
        JsonWriterMock.assert_called_once_with(path)
        JsonWriterMock.return_value.write.assert_called_once_with(data)


@patch.dict('sys.modules', atexit=MagicMock())
class TestTextReporting(TestCase):

    def test_write_reports_writes_text_report(self):
        p = Profiling(text_config(), None)
        p.write_text_report = MagicMock()
        p.write_reports()
        self.assertEqual(p.write_text_report.call_count, 1)

    def test_write_text_report_sends_data_to_textwriter(self):
        path = 'path/to/report.txt'
        data = MagicMock()
        with patch('profiling.profiling.TextWriter') as TextWriterMock:
            p = Profiling(text_config(path=path), None)
            p.write_text_report(data)
        TextWriterMock.assert_called_once_with(path)
        TextWriterMock.return_value.write.assert_called_once_with(data)
