from unittest import TestCase
from unittest.mock import MagicMock, Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.message import EndpointId

from k2.sut import SUT, SUT_RESET_DONE
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

from ..files import FILES_MONITOR_ENABLED, SystemFilesCollector, SystemFilesMonitorError, \
    SystemFileUsageMonitor

MOCK_ENDPOINT = EndpointId('mock', 'Mock endpoint')


class TestSystemFilesTicksCollector(TestCase):

    def setUp(self):
        self.exec = MagicMock()
        self.collector = SystemFilesCollector(self.exec)

    def test_raises_files_monitor_error_if_exec_raises(self):
        with self.assertRaisesRegex(SystemFilesMonitorError, 'Could not collect file usage data'):
            self.exec.send_line = MagicMock(side_effect=Exception('remote peer said no'))
            self.collector.collect()

    def test_raises_files_monitor_error_on_missing_data(self):
        with self.assertRaisesRegex(SystemFilesMonitorError, 'Could not collect file usage data'):
            self.exec.send_line = MagicMock(return_value='no file descriptor data here!')
            self.collector.collect()

    def test_can_parse_valid_files_ticks_data(self):
        self.exec.send_line = MagicMock(return_value=('12345 0 234567'))
        data = self.collector.collect()
        self.exec.send_line.assert_called_once_with('cat /proc/sys/fs/file-nr', timeout=5)
        assert data['opened'] == 12345
        assert data['max_allowed'] == 234567


class TestSystemFilesUsageMonitor(TestCase):

    def test_listens_for_collect_measurements_requests_if_enabled(self):
        with _create_harness(enabled=True) as harness:
            assert harness.any_registered_dispatchers(
                PERFORM_MEASUREMENT, MONITOR_ENDPOINT, entity='mysut')

    def test_perform_measurement(self):
        with _create_harness() as harness:
            harness.exec.send_line = MagicMock(side_effect=[
                '123 0 234',
                '125 0 239',
            ])
            for _ in range(2):
                request = harness.send_request(PERFORM_MEASUREMENT, MONITOR_ENDPOINT, data=None)
                request.wait()[0].result()
            harness.create_series_metric.assert_any_call('system.files.opened', 123)
            harness.create_series_metric.assert_any_call('system.files.max_allowed', 234)
            harness.create_series_metric.assert_any_call('system.files.opened', 125)
            harness.create_series_metric.assert_any_call('system.files.max_allowed', 239)


def _create_harness(enabled=True):
    config = ConfigManager()
    entity = 'mysut'
    config.set(SUT, [entity])
    config.set(FILES_MONITOR_ENABLED, enabled, entity=entity)

    exec = Mock()
    create_series_metric = Mock()
    harness = ExtensionTestHarness(
        SystemFileUsageMonitor,
        config=config,
        endpoints_and_messages={
            MONITOR_ENDPOINT: [PERFORM_MEASUREMENT],
            MOCK_ENDPOINT: [SUT_RESET_DONE],
        },
        components=[
            ComponentMock(name='Exec', mock=exec, can=['telnet']),
            ComponentMock(name='CreateSeriesMetric', mock=create_series_metric)
        ])
    harness.exec = exec
    harness.create_series_metric = create_series_metric
    return harness
