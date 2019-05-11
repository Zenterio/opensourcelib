from collections import Counter
from unittest import TestCase
from unittest.mock import MagicMock, Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.message import EndpointId

from k2.sut import SUT, SUT_RESET_DONE
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

from ..cpu import CPU_USAGE_MONITOR_ENABLED, SystemCpuMonitorError, SystemCpuTicksCollector, \
    SystemCpuUsage, SystemCpuUsageMonitor

MOCK_ENDPOINT = EndpointId('mock', 'Mock endpoint')


class TestSystemCpuTicksCollector(TestCase):

    def setUp(self):
        self.exec = MagicMock()
        self.collector = SystemCpuTicksCollector(self.exec)

    def test_raises_cpu_monitor_error_if_exec_raises(self):
        with self.assertRaisesRegex(SystemCpuMonitorError, 'Could not collect CPU ticks data'):
            self.exec.send_line = MagicMock(side_effect=Exception('remote peer said no'))
            self.collector.collect()

    def test_raises_cpu_monitor_error_on_missing_data(self):
        with self.assertRaisesRegex(SystemCpuMonitorError, 'Could not parse CPU ticks data'):
            self.exec.send_line = MagicMock(return_value='no CPU ticks data here!')
            self.collector.collect()

    def test_can_parse_valid_cpu_ticks_data(self):
        self.exec.send_line = MagicMock(
            return_value=(
                'cpu  91493690 0 7903253 87025397 7 1189 463640 0 0 0\n'
                'cpu0 43376692 0 3913975 45396376 4 1164 455494 0 0 0\n'
                'cpu1 48116998 0 3989278 41629020 2 24 8146 0 0 0\n'
                'intr 2765382081 0 0 28 0 95480767 0 0 0 0 0 5 0 0 0 0 0 7654693 0 0 0 175 0 5780 2305 3050113 0 0 0 0 0 0 15270 0 0 0 0 0 0 28667 0 0 0 0 0 0 24840 0 0 0 0 0 960694 1388761 0 0 0 0 0 1 1 0 0 0 1 1 95482118 0 4520 0 0 0 0 54361 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 21727425 14690821 0 0 0 0 0 2524810734 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n'  # noqa
                'ctxt 3443574968\n'
                'btime 1514465051\n'
                'processes 6609983\n'
                'procs_running 2\n'
                'procs_blocked 0\n'
                'softirq 1377782275 192071970 1070851072 538720 14807537 0 0 3031680 27234425 5357390 63889481'
            ))
        data = self.collector.collect()
        self.exec.send_line.assert_called_once_with('cat /proc/stat', timeout=5)
        assert data['user'] == 91493690
        assert data['system'] == 7903253
        assert data['idle'] == 87025397


class TestSystemCpuUsage(TestCase):

    def setUp(self):
        self.ticks_collector = MagicMock()
        self.ticks_collector.collect = MagicMock(
            return_value=Counter({
                'system': 0,
                'user': 0,
                'idle': 0
            }))
        self.collector = SystemCpuUsage(self.ticks_collector)

    def test_collects_a_measurement_when_collect_is_called(self):
        self.collector.collect()
        self.ticks_collector.collect.assert_called_once_with()

    def test_collect_zero_measurement(self):
        data = self.collector.collect()
        assert data['user'] == 0
        assert data['system'] == 0
        assert data['idle'] == 0

    def test_collect_returns_measurement_as_percentages(self):
        self.ticks_collector.collect = MagicMock(
            return_value=Counter({
                'system': 100,
                'user': 200,
                'idle': 700
            }))
        data = self.collector.collect()
        assert data['user'] == 20
        assert data['system'] == 10
        assert data['idle'] == 70


class TestSystemCpuUsageMonitor(TestCase):

    def test_listens_for_collect_measurements_requests_if_enabled(self):
        with _create_harness(enabled=True) as harness:
            assert harness.any_registered_dispatchers(
                PERFORM_MEASUREMENT, MONITOR_ENDPOINT, entity='mysut')

    def test_perform_measurement(self):
        with _create_harness() as harness:
            harness.exec.send_line = MagicMock(
                side_effect=[
                    'cpu  200 0 300 500 7 1189 463640 0 0 0',
                    'cpu  250 0 450 700 7 1189 463640 0 0 0'
                ])
            for _ in range(2):
                request = harness.send_request(PERFORM_MEASUREMENT, MONITOR_ENDPOINT, data=None)
                request.wait()[0].result()
            harness.create_series_metric.assert_any_call('system.cpu.user', 12.5)
            harness.create_series_metric.assert_any_call('system.cpu.system', 37.5)
            harness.create_series_metric.assert_any_call('system.cpu.idle', 50.0)

    def test_sut_reset_done(self):
        with _create_harness() as harness:
            harness.extension._first_iteration = False
            harness.trigger_event(SUT_RESET_DONE, MOCK_ENDPOINT, entity='mysut')
        assert harness.extension._first_iteration is True


def _create_harness(enabled=True):
    config = ConfigManager()
    entity = 'mysut'
    config.set(SUT, [entity])
    config.set(CPU_USAGE_MONITOR_ENABLED, enabled, entity=entity)

    exec = Mock()
    create_series_metric = Mock()
    harness = ExtensionTestHarness(
        SystemCpuUsageMonitor,
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
