from collections import Counter
from unittest import TestCase
from unittest.mock import MagicMock, Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.message import EndpointId

from k2.sut import SUT, SUT_RESET_DONE
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

from ..cpu import PROC_CPU_USAGE_MONITOR_IDS, PROC_CPU_USAGE_MONITOR_PATTERNS, \
    SUT_PROC_CPU_USAGE_MONITOR_IDS, ProcCpuMonitorError, ProcCpuUsage, ProcCpuUsageMonitor, \
    ProcStatusCollector

MOCK_ENDPOINT = EndpointId('mock', 'Mock endpoint')


class TestProcStatusCollector(TestCase):

    def setUp(self):
        self.exec = MagicMock()
        self.collector = ProcStatusCollector(self.exec)

    def test_raises_proc_cpu_monitor_error_if_exec_raises(self):
        with self.assertRaisesRegex(ProcCpuMonitorError,
                                    'Could not collect status data for process with PID 1'):
            self.exec.send_line = MagicMock(side_effect=Exception('/bin/sh: cat: not found'))
            self.collector.collect(1)

    def test_raises_proc_cpu_monitor_error_if_unable_to_parse_data(self):
        with self.assertRaisesRegex(ProcCpuMonitorError,
                                    'Could not parse status data for process with PID 1'):
            self.exec.send_line = MagicMock(return_value='nope')
            self.collector.collect(1)

    def test_parse_some_data(self):
        self.exec.send_line = MagicMock(
            return_value=(
                '1 (mtdblock2) S -1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 '
                '18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 '
                '38 39 40 41 42 43 44'))
        data = self.collector.collect(1)
        self.exec.send_line.assert_called_once_with('cat /proc/1/stat', timeout=5)
        assert data == {
            'pid': 1,
            'state': 'S',
            'ppid': -1,
            'pgrp': 2,
            'session': 3,
            'tty_nr': 4,
            'tpgid': 5,
            'flags': 6,
            'minflt': 7,
            'cminflt': 8,
            'majflt': 9,
            'cmajflt': 10,
            'utime': 11,
            'stime': 12,
            'cutime': 13,
            'cstime': 14,
            'priority': 15,
            'nice': 16,
            'num_threads': 17,
            'itrealvalue': 18,
            'starttime': 19,
            'vsize': 20,
            'rss': 21,
            'rsslim': 22,
            'startcode': 23,
            'endcode': 24,
            'startstack': 25,
            'kstkesp': 26,
            'kstkeip': 27,
            'signal': 28,
            'blocked': 29,
            'sigignore': 30,
            'sigcatch': 31,
            'wchan': 32,
            'nswap': 33,
            'cnswap': 34,
            'exit_signal': 35
        }


class TestProcCpuUsage(TestCase):

    def setUp(self):
        self.system_cpu_ticks_collector = MagicMock()
        self.system_cpu_ticks_collector.collect = MagicMock(
            return_value=Counter({
                'system': 0,
                'user': 0,
                'idle': 0,
            }))

        self.proc_status_collector = MagicMock()
        self.proc_status_collector.collect = MagicMock(
            return_value={
                'utime': 0,
                'stime': 0,
                'cutime': 0,
                'cstime': 0,
            })

        self.collector = ProcCpuUsage(self.system_cpu_ticks_collector, self.proc_status_collector)

    def test_collects_a_measurement_when_collect_is_called(self):
        self.collector.collect(1)
        self.system_cpu_ticks_collector.collect.assert_called_once_with()
        self.proc_status_collector.collect.assert_called_once_with(1)

    def test_collect_zero_measurement(self):
        data = self.collector.collect(1)
        assert data['utime'] == 0
        assert data['stime'] == 0
        assert data['cutime'] == 0
        assert data['cstime'] == 0

    def test_collect_with_no_child_activity(self):
        self.system_cpu_ticks_collector.collect = MagicMock(
            return_value=Counter({
                'system': 40,
                'user': 50,
                'idle': 10,
            }))

        self.proc_status_collector.collect = MagicMock(
            return_value={
                'utime': 4,
                'stime': 5,
                'cutime': 0,
                'cstime': 0,
            })

        data = self.collector.collect(1)
        assert data['utime'] == 4
        assert data['stime'] == 5
        assert data['cutime'] == 0
        assert data['cstime'] == 0

    def test_collect_with_child_activity(self):
        self.system_cpu_ticks_collector.collect = MagicMock(
            return_value=Counter({
                'system': 40,
                'user': 50,
                'idle': 10,
            }))

        self.proc_status_collector.collect = MagicMock(
            return_value={
                'utime': 1,
                'stime': 2,
                'cutime': 3,
                'cstime': 4,
            })

        data = self.collector.collect(1)
        assert data['utime'] == 1
        assert data['stime'] == 2
        assert data['cutime'] == 3
        assert data['cstime'] == 4


class TestProcCpuUsageMonitor(TestCase):

    def test_listens_for_collect_measurements_requests_if_enabled(self):
        with _create_harness() as harness:
            assert harness.any_registered_dispatchers(
                PERFORM_MEASUREMENT, MONITOR_ENDPOINT, entity='mysut')

    def test_perform_measurement(self):
        with _create_harness() as harness:
            harness.exec.send_line = MagicMock(
                side_effect=[
                    (
                        '1 (mtdblock2) S -1 2 3 4 5 6 7 8 9 10 10 20 30 40 15 16 17 '
                        '18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 '
                        '38 39 40 41 42 43 44'),
                    (
                        '1 (mtdblock2) S -1 2 3 4 5 6 7 8 9 10 40 60 80 100 15 16 17 '
                        '18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 '
                        '38 39 40 41 42 43 44'),
                    (
                        '1 (mtdblock2) S -1 2 3 4 5 6 7 8 9 10 80 110 140 170 15 16 17 '
                        '18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 '
                        '38 39 40 41 42 43 44'),
                    (
                        '1 (mtdblock2) S -1 2 3 4 5 6 7 8 9 10 130 170 210 250 15 16 17 '
                        '18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 '
                        '38 39 40 41 42 43 44'),
                ])
            harness.proc_pid_collector.collect = MagicMock(return_value=[1, 2])
            harness.system_cpu_ticks_collector.collect = MagicMock(
                side_effect=[
                    Counter({
                        'user': 40,
                        'system': 100,
                        'idle': 60
                    }),
                    Counter({
                        'user': 80,
                        'system': 200,
                        'idle': 120
                    }),
                    Counter({
                        'user': 80,
                        'system': 200,
                        'idle': 120
                    }),
                    Counter({
                        'user': 120,
                        'system': 300,
                        'idle': 180
                    }),
                ])
            harness.extension._first_iteration = False
            request = harness.send_request(PERFORM_MEASUREMENT, MONITOR_ENDPOINT, data=None)
            request.wait()[0].result()
            print(harness.create_series_metric.call_args_list)
            harness.create_series_metric.assert_any_call('proc.cpu.mymonitor.utime.1.0', 5.0)
            harness.create_series_metric.assert_any_call('proc.cpu.mymonitor.stime.1.0', 10.0)
            harness.create_series_metric.assert_any_call('proc.cpu.mymonitor.cutime.1.0', 15.0)
            harness.create_series_metric.assert_any_call('proc.cpu.mymonitor.cstime.1.0', 20.0)
            harness.create_series_metric.assert_any_call('proc.cpu.mymonitor.utime.2.0', 10.0)
            harness.create_series_metric.assert_any_call('proc.cpu.mymonitor.stime.2.0', 15.0)
            harness.create_series_metric.assert_any_call('proc.cpu.mymonitor.cutime.2.0', 20.0)
            harness.create_series_metric.assert_any_call('proc.cpu.mymonitor.cstime.2.0', 25.0)
            harness.create_series_metric.assert_any_call('proc.cpu.myothermonitor.utime.1.0', 35.0)
            harness.create_series_metric.assert_any_call('proc.cpu.myothermonitor.stime.1.0', 45.0)
            harness.create_series_metric.assert_any_call('proc.cpu.myothermonitor.cutime.1.0', 55.0)
            harness.create_series_metric.assert_any_call('proc.cpu.myothermonitor.cstime.1.0', 65.0)
            harness.create_series_metric.assert_any_call('proc.cpu.myothermonitor.utime.2.0', 45.0)
            harness.create_series_metric.assert_any_call('proc.cpu.myothermonitor.stime.2.0', 55.0)
            harness.create_series_metric.assert_any_call('proc.cpu.myothermonitor.cutime.2.0', 65.0)
            harness.create_series_metric.assert_any_call('proc.cpu.myothermonitor.cstime.2.0', 75.0)

    def test_reset_count_is_incremented_on_reset_done(self):
        with _create_harness() as harness:
            assert harness.extension._reset_count == 0
            harness.trigger_event(SUT_RESET_DONE, MOCK_ENDPOINT, entity='mysut')
            assert harness.extension._reset_count == 1

    def test_sut_reset_done(self):
        with _create_harness() as harness:
            harness.extension._first_iteration = False
            harness.trigger_event(SUT_RESET_DONE, MOCK_ENDPOINT, entity='mysut')
        assert harness.extension._first_iteration is True


def _create_harness():
    config = ConfigManager()
    entity = 'mysut'
    config.set(SUT, [entity])
    config.set(SUT_PROC_CPU_USAGE_MONITOR_IDS, ['mymonitor', 'myothermonitor'], entity=entity)
    config.set(PROC_CPU_USAGE_MONITOR_IDS, ['mymonitor', 'myothermonitor'])
    config.set(PROC_CPU_USAGE_MONITOR_PATTERNS, ['my_pattern'], entity='mymonitor')
    config.set(PROC_CPU_USAGE_MONITOR_PATTERNS, ['my_other_pattern'], entity='myothermonitor')

    exec = Mock()
    system_cpu_ticks_collector = Mock()
    proc_pid_collector = Mock()
    create_series_metric = Mock()
    harness = ExtensionTestHarness(
        ProcCpuUsageMonitor,
        config=config,
        endpoints_and_messages={
            MONITOR_ENDPOINT: [PERFORM_MEASUREMENT],
            MOCK_ENDPOINT: [SUT_RESET_DONE],
        },
        components=[
            ComponentMock(name='Exec', mock=exec, can=['telnet']),
            ComponentMock(name='SystemCpuTicksCollector', mock=system_cpu_ticks_collector),
            ComponentMock(name='ProcPidCollector', mock=proc_pid_collector),
            ComponentMock(name='CreateSeriesMetric', mock=create_series_metric)
        ])
    harness.exec = exec
    harness.system_cpu_ticks_collector = system_cpu_ticks_collector
    harness.proc_pid_collector = proc_pid_collector
    harness.create_series_metric = create_series_metric
    return harness
