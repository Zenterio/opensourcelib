from unittest import TestCase
from unittest.mock import MagicMock, Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2.sut import SUT
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT

from ..mem import SYSTEM_MEMORY_USAGE_MONITOR_ENABLED, SystemMemoryMonitorError, \
    SystemMemoryUsageCollector, SystemMemoryUsageMonitor


class TestSystemMemoryUsageCollector(TestCase):

    def setUp(self):
        self.exec = MagicMock()
        self.collector = SystemMemoryUsageCollector(self.exec)

    def test_raises_system_memory_monitor_error_if_exec_raises(self):
        with self.assertRaisesRegex(SystemMemoryMonitorError,
                                    'Could not collect system memory usage data'):
            self.exec.send_line = MagicMock(side_effect=Exception('remote peer said no'))
            self.collector.collect()

    def test_raises_system_memory_monitor_error_on_missing_data(self):
        with self.assertRaisesRegex(SystemMemoryMonitorError,
                                    'Could not parse system memory usage data'):
            self.exec.send_line = MagicMock(return_value='No sysmem data here!')
            self.collector.collect()

    def test_can_parse_valid_sysmem_data(self):
        self.exec.send_line = MagicMock(
            return_value=(
                'MemTotal:         705252 kB\n'
                'MemFree:          461948 kB\n'
                'Buffers:           38244 kB\n'
                'Cached:           112200 kB\n'
                'SwapCached:            0 kB\n'
                'Active:            32532 kB\n'
                'Inactive:         139552 kB\n'
                'Active(anon):      22268 kB\n'
                'Inactive(anon):      332 kB\n'
                'Active(file):      10264 kB\n'
                'Inactive(file):   139220 kB\n'
                'Unevictable:           0 kB\n'
                'Mlocked:               0 kB\n'
                'SwapTotal:             0 kB\n'
                'SwapFree:              0 kB\n'
                'Dirty:                 0 kB\n'
                'Writeback:             0 kB\n'
                'AnonPages:         21724 kB\n'
                'Mapped:            43848 kB\n'
                'Shmem:               960 kB\n'
                'Slab:              14904 kB\n'
                'SReclaimable:       4480 kB\n'
                'SUnreclaim:        10424 kB\n'
                'KernelStack:        1456 kB\n'
                'PageTables:         1268 kB\n'
                'NFS_Unstable:          0 kB\n'
                'Bounce:                0 kB\n'
                'WritebackTmp:          0 kB\n'
                'CommitLimit:      352624 kB\n'
                'Committed_AS:     219328 kB\n'
                'VmallocTotal:     509876 kB\n'
                'VmallocUsed:        9372 kB\n'
                'VmallocChunk:     487412 kB\n'))
        data = self.collector.collect()
        self.exec.send_line.assert_called_once_with('cat /proc/meminfo', timeout=5)
        assert data['free'] == 461948
        assert data['buffers'] == 38244
        assert data['cached'] == 112200


class TestSystemMemoryUsageMonitor(TestCase):

    def test_listens_for_collect_measurements_requests_if_enabled(self):
        with _create_harness(enabled=True) as harness:
            assert harness.any_registered_dispatchers(
                PERFORM_MEASUREMENT, MONITOR_ENDPOINT, entity='mysut')

    def test_perform_measurement(self):
        with _create_harness() as harness:
            harness.exec.send_line = MagicMock(
                return_value=(
                    'MemFree:               1 kB\n'
                    'Buffers:               2 kB\n'
                    'Cached:                3 kB\n'))
            request = harness.send_request(PERFORM_MEASUREMENT, MONITOR_ENDPOINT, data=None)
            request.wait()[0].result()
            harness.create_series_metric.assert_any_call('system.memory.free', 1)
            harness.create_series_metric.assert_any_call('system.memory.buffers', 2)
            harness.create_series_metric.assert_any_call('system.memory.cached', 3)


def _create_harness(enabled=True):
    config = ConfigManager()
    entity = 'mysut'
    config.set(SUT, [entity])
    config.set(SYSTEM_MEMORY_USAGE_MONITOR_ENABLED, enabled, entity=entity)

    exec = Mock()
    create_series_metric = Mock()
    harness = ExtensionTestHarness(
        SystemMemoryUsageMonitor,
        config=config,
        endpoints_and_messages={MONITOR_ENDPOINT: [PERFORM_MEASUREMENT]},
        components=[
            ComponentMock(name='Exec', mock=exec, can=['telnet']),
            ComponentMock(name='CreateSeriesMetric', mock=create_series_metric)
        ])
    harness.exec = exec
    harness.create_series_metric = create_series_metric
    return harness
