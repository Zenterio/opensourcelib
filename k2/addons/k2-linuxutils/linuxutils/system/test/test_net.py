from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.message import EndpointId

import linuxutils.system.net  # noqa
from k2.sut import SUT, SUT_RESET_DONE
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

from ..net import SYSTEM_NETWORK_USAGE_MONITOR_ENABLED, SystemNetworkMonitorError, \
    SystemNetworkStatistics, SystemNetworkStatisticsCollector, SystemNetworkUsageMonitor

# flake8: noqa: E501

MOCK_ENDPOINT = EndpointId('mock', 'Mock endpoint')


class TestSystemNetworkStatisticsCollector(TestCase):

    def setUp(self):
        self.exec = MagicMock()
        self.collector = SystemNetworkStatisticsCollector(self.exec)

    def test_raises_system_network_monitor_error_if_exec_raises(self):
        with self.assertRaisesRegex(SystemNetworkMonitorError,
                                    'Could not collect network statistics'):
            self.exec.send_line = MagicMock(side_effect=Exception('/bin/sh: cat: not found'))
            self.collector.collect()

    def test_raises_proc_cpu_monitor_error_if_unable_to_parse_data(self):
        with self.assertRaisesRegex(SystemNetworkMonitorError,
                                    'Could not parse network statistics'):
            self.exec.send_line = MagicMock(return_value='nope')
            self.collector.collect()

    def test_parse_some_data(self):
        self.exec.send_line = MagicMock(
            return_value=(
                'Inter-|   Receive                                                |  Transmit\n'
                ' face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed\n'
                '    lo: 2119688   27890    1    2    3     4          5         6  2119688   27890    7    8    9    10      11         12\n'
                '  eth0: 181175786  812500   13   14   15    16         17    293059 11646304  101360   18   19   20    21      22         23'
            ))
        data = self.collector.collect()
        self.exec.send_line.assert_called_once_with('cat /proc/net/dev', timeout=5)
        assert data == {
            'lo': {
                'rx_bytes': 2119688,
                'rx_packets': 27890,
                'rx_errs': 1,
                'rx_drop': 2,
                'rx_fifo': 3,
                'rx_frame': 4,
                'rx_compressed': 5,
                'rx_multicast': 6,
                'tx_bytes': 2119688,
                'tx_packets': 27890,
                'tx_errs': 7,
                'tx_drop': 8,
                'tx_fifo': 9,
                'tx_colls': 10,
                'tx_carrier': 11,
                'tx_compressed': 12,
            },
            'eth0': {
                'rx_bytes': 181175786,
                'rx_packets': 812500,
                'rx_errs': 13,
                'rx_drop': 14,
                'rx_fifo': 15,
                'rx_frame': 16,
                'rx_compressed': 17,
                'rx_multicast': 293059,
                'tx_bytes': 11646304,
                'tx_packets': 101360,
                'tx_errs': 18,
                'tx_drop': 19,
                'tx_fifo': 20,
                'tx_colls': 21,
                'tx_carrier': 22,
                'tx_compressed': 23,
            },
        }


class TestSystemNetworkStatistics(TestCase):

    def setUp(self):
        self.system_network_statisitcs_collector = MagicMock()
        self.system_network_statisitcs_collector.collect = MagicMock(
            return_value={
                'lo': {
                    'rx_bytes': 0,
                    'tx_bytes': 0,
                },
                'eth0': {
                    'rx_bytes': 0,
                    'tx_bytes': 0,
                }
            })

        self.collector = SystemNetworkStatistics(self.system_network_statisitcs_collector)

    def test_collects_a_measurement_when_collect_is_called(self):
        self.collector.collect()
        self.system_network_statisitcs_collector.collect.assert_called_with()

    def test_collect_zero_measurement(self):
        data = self.collector.collect()
        assert data == {
            'lo': {
                'rx_kbps': 0,
                'tx_kbps': 0
            },
            'eth0': {
                'rx_kbps': 0,
                'tx_kbps': 0
            },
        }

    def test_collect_with_some_activity(self):
        self.system_network_statisitcs_collector.collect = MagicMock(
            side_effect=[
                {
                    'lo': {
                        'rx_bytes': 10 * 1024,
                        'tx_bytes': 20 * 1024,
                    },
                    'eth0': {
                        'rx_bytes': 30 * 1024,
                        'tx_bytes': 40 * 1024,
                    }
                },
                {
                    'lo': {
                        'rx_bytes': 20 * 1024,
                        'tx_bytes': 40 * 1024,
                    },
                    'eth0': {
                        'rx_bytes': 60 * 1024,
                        'tx_bytes': 80 * 1024,
                    }
                },
            ])
        with patch('linuxutils.system.net.time', new=MagicMock(side_effect=[10, 20])):
            self.collector.collect()
            data = self.collector.collect()
        assert data == {
            'lo': {
                'rx_kbps': 1,
                'tx_kbps': 2
            },
            'eth0': {
                'rx_kbps': 3,
                'tx_kbps': 4
            },
        }


class TestProcNetworkUsageMonitor(TestCase):

    def test_listens_for_collect_measurements_requests_if_enabled(self):
        with _create_harness() as harness:
            assert harness.any_registered_dispatchers(
                PERFORM_MEASUREMENT, MONITOR_ENDPOINT, entity='mysut')

    def test_perform_measurement(self):
        with _create_harness() as harness:
            harness.exec.send_line = MagicMock(
                side_effect=[
                    (
                        'Inter-|   Receive                                                |  Transmit\n'
                        ' face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed\n'
                        '    lo: 10240            0    0    0    0     0          0         0  30720            0    0    0    0     0       0          0\n'
                        '  eth0: 20480            0    0    0    0     0          0         0  20480            0    0    0    0     0       0          0'
                    ),
                    (
                        'Inter-|   Receive                                                |  Transmit\n'
                        ' face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed\n'
                        '    lo: 20480            0    0    0    0     0          0         0  30720            0    0    0    0     0       0          0\n'
                        '  eth0: 30720            0    0    0    0     0          0         0  51200            0    0    0    0     0       0          0'
                    ),
                ])
            with patch('linuxutils.system.net.time', new=MagicMock(side_effect=[10, 20])):
                harness.send_request(PERFORM_MEASUREMENT, MONITOR_ENDPOINT, data=None)
                request = harness.send_request(PERFORM_MEASUREMENT, MONITOR_ENDPOINT, data=None)
                request.wait()[0].result()
            harness.create_series_metric.assert_any_call('system.network.lo.rx_kbps', 1)
            harness.create_series_metric.assert_any_call('system.network.lo.tx_kbps', 0)
            harness.create_series_metric.assert_any_call('system.network.eth0.rx_kbps', 1)
            harness.create_series_metric.assert_any_call('system.network.eth0.tx_kbps', 3)

    def test_sut_reset_done(self):
        with _create_harness() as harness:
            harness.extension._first_iteration = False
            harness.trigger_event(SUT_RESET_DONE, MOCK_ENDPOINT, entity='mysut')
        assert harness.extension._first_iteration is True


def _create_harness(enabled=True):
    config = ConfigManager()
    entity = 'mysut'
    config.set(SUT, [entity])
    config.set(SYSTEM_NETWORK_USAGE_MONITOR_ENABLED, enabled, entity=entity)

    exec = Mock()
    create_series_metric = Mock()
    harness = ExtensionTestHarness(
        SystemNetworkUsageMonitor,
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
