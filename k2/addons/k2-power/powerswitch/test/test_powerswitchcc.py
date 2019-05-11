from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from connectioncheck import CONNECTIONCHECK_RUN_CHECK
from k2.sut import SUT
from powerswitch import AVAILABLE_POWER_SWITCHES

from ..powerswitchcc import POWER_SWITCH, POWER_SWITCH_CONNECTION_CHECK_ENABLED, \
    POWER_SWITCH_CONNECTION_CHECK_ENDPOINT, POWER_SWITCH_CONNECTION_CHECK_REQUIRED, \
    PowerSwitchConnectionCheck


class TestPowerSwitchConnectionCheck(TestCase):

    def test_extension_registers_dispatchers(self):
        with create_harness() as harness:
            assert harness.messagebus.has_registered_dispatchers(
                CONNECTIONCHECK_RUN_CHECK, POWER_SWITCH_CONNECTION_CHECK_ENDPOINT, 'entity')

    def test_run_check_triggers_powerswitch_client_to_be_created_and_test_command_send(self):
        with patch('powerswitch.powerswitchcc.PowerSwitch', new=MagicMock()):
            with create_harness() as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK,
                    POWER_SWITCH_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert result.success

    def test_run_check_fails_if_powerswitch_client_raises_exception(self):
        client = MagicMock()
        mock = Mock()
        mock.side_effect = Exception('fail')
        client.state = mock
        with patch('powerswitch.powerswitchcc.PowerSwitch', return_value=client):
            with create_harness() as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK,
                    POWER_SWITCH_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert not result.success

    def test_run_check_reports_not_required_if_configured(self):
        with patch('powerswitch.powerswitchcc.PowerSwitch', new=MagicMock()):
            with create_harness(powerswitch_cc_required=True) as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK,
                    POWER_SWITCH_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert result.required
            with create_harness(powerswitch_cc_required=False) as harness:
                result = harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECK,
                    POWER_SWITCH_CONNECTION_CHECK_ENDPOINT,
                    entity='entity').wait(timeout=1)[0].result(timeout=0)
                assert not result.required


def create_harness(
        powerswitch='gude', powerswitch_cc_enabled=True, powerswitch_cc_required=True,
        sut=['entity']):

    config = ConfigManager()
    entity = sut[0]
    config.set(SUT, sut)
    config.set(AVAILABLE_POWER_SWITCHES, ['gude'])
    config.set(POWER_SWITCH, powerswitch, entity=entity)
    config.set(POWER_SWITCH_CONNECTION_CHECK_ENABLED, powerswitch_cc_enabled, entity=entity)
    config.set(POWER_SWITCH_CONNECTION_CHECK_REQUIRED, powerswitch_cc_required, entity=entity)

    return ExtensionTestHarness(PowerSwitchConnectionCheck, config=config)
