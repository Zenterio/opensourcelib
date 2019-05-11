from unittest import TestCase
from unittest.mock import MagicMock, Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2 import EndpointId
from k2.sut import SUT, SUT_RESET_DONE
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

from ..mem import PROC_MEMORY_USAGE_MONITOR_IDS, PROC_MEMORY_USAGE_MONITOR_PATTERNS, \
    SUT_PROC_MEMORY_USAGE_MONITOR_IDS, ProcMemoryMonitorError, ProcMemoryUsageCollector, \
    ProcMemoryUsageMonitor

MOCK_ENDPOINT = EndpointId('mock', 'Mock endpoint')


class TestProcMemoryUsageCollector(TestCase):

    def setUp(self):
        self.exec = MagicMock()
        self.collector = ProcMemoryUsageCollector(self.exec)

    def test_raises_proc_memory_monitor_error_if_exec_raises(self):
        with self.assertRaisesRegex(ProcMemoryMonitorError,
                                    'Could not collect memory stats for process with PID 1'):
            self.exec.send_line = MagicMock(side_effect=Exception('/bin/sh: cat: not found'))
            self.collector.collect(1)

    def test_raises_proc_memory_monitor_error_if_unable_to_parse_data(self):
        with self.assertRaisesRegex(ProcMemoryMonitorError,
                                    'Could not parse memory stats for process with PID 1'):
            self.exec.send_line = MagicMock(return_value='nope')
            self.collector.collect(1)

    def test_parse_some_data(self):
        self.exec.send_line = MagicMock(return_value='1 2 3 4 5 6 7')
        data = self.collector.collect(1)
        self.exec.send_line.assert_called_once_with('cat /proc/1/statm', timeout=5)
        assert data == {
            'size': 1 * 4,
            'resident': 2 * 4,
            'shared': 3 * 4,
            'text': 4 * 4,
            'lib': 5 * 4,
            'data': 6 * 4,
            'dt': 7 * 4,
        }


class TestProcMemoryUsageMonitor(TestCase):

    def test_listens_for_collect_measurements_requests_if_enabled(self):
        with _create_harness() as harness:
            assert harness.any_registered_dispatchers(
                PERFORM_MEASUREMENT, MONITOR_ENDPOINT, entity='mysut')

    def test_perform_measurement(self):
        with _create_harness() as harness:
            harness.exec.send_line = MagicMock(
                side_effect=[
                    '1 2 3 4 5 6 7',
                    '2 3 4 5 6 7 8',
                    '3 4 5 6 7 8 9',
                    '4 5 6 7 8 9 10',
                ])
            harness.proc_pid_collector.collect = MagicMock(return_value=[1, 2])
            request = harness.send_request(PERFORM_MEASUREMENT, MONITOR_ENDPOINT, data=None)
            request.wait()[0].result()
            harness.create_series_metric.assert_any_call('proc.memory.mymonitor.size.1.0', 4)
            harness.create_series_metric.assert_any_call('proc.memory.mymonitor.resident.1.0', 8)
            harness.create_series_metric.assert_any_call('proc.memory.mymonitor.size.2.0', 8)
            harness.create_series_metric.assert_any_call('proc.memory.mymonitor.resident.2.0', 12)
            harness.create_series_metric.assert_any_call('proc.memory.myothermonitor.size.1.0', 12)
            harness.create_series_metric.assert_any_call(
                'proc.memory.myothermonitor.resident.1.0', 16)
            harness.create_series_metric.assert_any_call('proc.memory.myothermonitor.size.2.0', 16)
            harness.create_series_metric.assert_any_call(
                'proc.memory.myothermonitor.resident.2.0', 20)

    def test_reset_count_is_incremented_on_reset_done(self):
        with _create_harness() as harness:
            assert harness.extension._reset_count == 0
            harness.trigger_event(SUT_RESET_DONE, MOCK_ENDPOINT, entity='mysut')
            assert harness.extension._reset_count == 1


def _create_harness():
    config = ConfigManager()
    entity = 'mysut'
    config.set(SUT, [entity])
    config.set(SUT_PROC_MEMORY_USAGE_MONITOR_IDS, ['mymonitor', 'myothermonitor'], entity=entity)
    config.set(PROC_MEMORY_USAGE_MONITOR_IDS, ['mymonitor', 'myothermonitor'])
    config.set(PROC_MEMORY_USAGE_MONITOR_PATTERNS, ['my_pattern'], entity='mymonitor')
    config.set(PROC_MEMORY_USAGE_MONITOR_PATTERNS, ['my_other_pattern'], entity='myothermonitor')

    exec = Mock()
    proc_pid_collector = Mock()
    create_series_metric = Mock()
    harness = ExtensionTestHarness(
        ProcMemoryUsageMonitor,
        config=config,
        endpoints_and_messages={
            MONITOR_ENDPOINT: [PERFORM_MEASUREMENT],
            MOCK_ENDPOINT: [SUT_RESET_DONE]
        },
        components=[
            ComponentMock(name='Exec', mock=exec, can=['telnet']),
            ComponentMock(name='ProcPidCollector', mock=proc_pid_collector),
            ComponentMock(name='CreateSeriesMetric', mock=create_series_metric)
        ])
    harness.exec = exec
    harness.proc_pid_collector = proc_pid_collector
    harness.create_series_metric = create_series_metric
    return harness
