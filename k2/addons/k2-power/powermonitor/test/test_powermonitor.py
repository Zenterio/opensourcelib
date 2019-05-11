from unittest import TestCase
from unittest.mock import MagicMock, Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2.sut import SUT
from monitor import MONITOR_ENDPOINT, PERFORM_MEASUREMENT
from powermeter import AVAILABLE_POWER_METERS, POWER_METER

from ..powermonitor import POWER_CONSUMPTION_MONITOR_ENABLED, PowerConsumptionCollector, \
    PowerConsumptionMonitor, PowerConsumptionMonitorError


class TestPowerConsumptionCollector(TestCase):

    def setUp(self):
        self.powermeter = MagicMock()
        self.collector = PowerConsumptionCollector(self.powermeter)

    def test_raises_power_consumption_monitor_error_if_power_meter_raises(self):
        with self.assertRaises(PowerConsumptionMonitorError):
            self.powermeter.power = MagicMock(side_effect=Exception('Not supported'))
            self.collector.collect()

    def test_collect_power_consumption(self):
        power = 42
        self.powermeter.power = MagicMock(return_value=power)
        assert self.collector.collect() == power


class TestPowerConsumptionMonitor(TestCase):

    def test_listens_for_collect_measurements_requests_if_enabled(self):
        with _create_harness(enabled=True) as harness:
            assert harness.any_registered_dispatchers(
                PERFORM_MEASUREMENT, MONITOR_ENDPOINT, entity='mysut')

    def test_perform_measurement(self):
        with _create_harness() as harness:
            power = 42
            harness.powermeter.power = MagicMock(return_value=power)
            request = harness.send_request(PERFORM_MEASUREMENT, MONITOR_ENDPOINT, data=None)
            request.wait()[0].result()
            harness.create_series_metric.assert_any_call('system.power.active', power)


def _create_harness(enabled=True):
    config = ConfigManager()
    entity = 'mysut'
    config.set(SUT, [entity])
    config.set(AVAILABLE_POWER_METERS, ['fake_power_meter'])
    config.set(POWER_CONSUMPTION_MONITOR_ENABLED, enabled, entity=entity)
    config.set(POWER_METER, 'fake_power_meter', entity=entity)

    powermeter = Mock()
    create_series_metric = Mock()
    harness = ExtensionTestHarness(
        PowerConsumptionMonitor,
        config=config,
        endpoints_and_messages={MONITOR_ENDPOINT: [PERFORM_MEASUREMENT]},
        components=[
            ComponentMock(name='PowerMeter', mock=powermeter),
            ComponentMock(name='CreateSeriesMetric', mock=create_series_metric)
        ])
    harness.powermeter = powermeter
    harness.create_series_metric = create_series_metric
    return harness
