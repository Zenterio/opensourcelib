from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from connectioncheck import CONNECTIONCHECK_RUN_CHECK
from k2.sut import SUT
from powermeter import AVAILABLE_POWER_METERS

from ..powermetercc import POWER_METER, POWER_METER_CONNECTION_CHECK_ENABLED, \
    POWER_METER_CONNECTION_CHECK_ENDPOINT, POWER_METER_CONNECTION_CHECK_REQUIRED, \
    PowerMeterConnectionCheck


class TestPowerMeterConnectionCheck(TestCase):

    def test_extension_registers_dispatchers(self):
        with create_harness() as harness:
            assert harness.messagebus.has_registered_dispatchers(
                CONNECTIONCHECK_RUN_CHECK, POWER_METER_CONNECTION_CHECK_ENDPOINT, 'entity')

    def test_run_check_triggers_powermeter_client_to_be_created_and_test_command_send(self):
        with patch('powermeter.powermetercc.PowerMeter', new=MagicMock()):
            with create_harness() as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK,
                    POWER_METER_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert result.success

    def test_run_check_fails_if_powermeter_client_raises_exception(self):
        client = MagicMock()
        mock = Mock()
        mock.side_effect = Exception('fail')
        client.power = mock
        with patch('powermeter.powermetercc.PowerMeter', return_value=client):
            with create_harness() as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK,
                    POWER_METER_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert not result.success

    def test_run_check_reports_not_required_if_configured(self):
        with patch('powermeter.powermetercc.PowerMeter', new=MagicMock()):
            with create_harness(powermeter_cc_required=True) as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK,
                    POWER_METER_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert result.required
            with create_harness(powermeter_cc_required=False) as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK,
                    POWER_METER_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert not result.required


def create_harness(
        powermeter='gude', powermeter_cc_enabled=True, powermeter_cc_required=True, sut=['entity']):
    config = ConfigManager()
    entity = sut[0]
    config.set(SUT, sut)
    config.set(AVAILABLE_POWER_METERS, ['gude'])
    config.set(POWER_METER, powermeter, entity=entity)
    config.set(POWER_METER_CONNECTION_CHECK_ENABLED, powermeter_cc_enabled, entity=entity)
    config.set(POWER_METER_CONNECTION_CHECK_REQUIRED, powermeter_cc_required, entity=entity)

    return ExtensionTestHarness(PowerMeterConnectionCheck, config=config)
