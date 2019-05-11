from unittest import TestCase

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2.sut import SUT
from powermeter import AVAILABLE_POWER_METERS, POWER_METER, POWER_METER_POWER

from .. import DUMMY_POWER_METER_VALUE
from ..dummypowermeter import DummyPowerMeter


class TestDummyPowerMeter(TestCase):

    def test_not_enabled_if_powermeter_config_is_not_gude(self):
        with TestDummyPowerMeter._create_harness(power_meter='notgude') as harness:
            assert not harness.extension.is_active

    def test_enabled_if_powermeter_config_is_gude(self):
        with TestDummyPowerMeter._create_harness() as harness:
            assert harness.extension.is_active

    def test_correct_default_value(self):
        with TestDummyPowerMeter._create_harness() as h:
            futures = h.send_request(POWER_METER_POWER, entity='entity')
            futures.wait(timeout=1)
            assert futures[0].result(timeout=1) == 4.2

    def test_correct_custom_value(self):
        with TestDummyPowerMeter._create_harness(value=0.42) as h:
            futures = h.send_request(POWER_METER_POWER, entity='entity')
            futures.wait(timeout=1)
            assert futures[0].result(timeout=1) == 0.42

    @staticmethod
    def _create_harness(sut=['entity'], power_meter='dummy', value=4.2):
        config = ConfigManager()
        entity = sut[0]
        config.set(SUT, sut)
        config.set(AVAILABLE_POWER_METERS, ['dummy', 'notgude'])
        config.set(POWER_METER, power_meter, entity=entity)
        config.set(DUMMY_POWER_METER_VALUE, value, entity=entity)

        return ExtensionTestHarness(DummyPowerMeter, config=config)
