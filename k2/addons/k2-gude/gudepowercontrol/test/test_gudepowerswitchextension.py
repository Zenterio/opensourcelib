from unittest import TestCase
from unittest.mock import patch

from zaf.config import MissingConditionalConfigOption

from powerswitch import POWER_SWITCH_POWER_STATE, POWER_SWITCH_POWEROFF, POWER_SWITCH_POWERON

from .utils import create_powerswitch_harness, success_response


class TestGudePowerSwitchExtension(TestCase):

    def test_not_enabled_if_powerswitch_config_is_not_gude(self):
        with create_powerswitch_harness(power_switch='notgude') as harness:
            assert not harness.extension.is_active

    def test_enabled_if_powerswitch_config_is_gude(self):
        with create_powerswitch_harness() as harness:
            assert harness.extension.is_active

    def test_initialize_raises_exception_if_ip_or_port_is_missing(self):
        with self.assertRaises(MissingConditionalConfigOption):
            harness = create_powerswitch_harness(gude_ip=None)
            harness.__enter__()

        with self.assertRaises(MissingConditionalConfigOption):
            harness = create_powerswitch_harness(gude_port=None)
            harness.__enter__()

    def test_sends_http_request_with_state_1_when_receiving_poweron_requests(self):
        with create_powerswitch_harness() as h:
            with patch('requests.get', return_value=success_response()) as m:
                futures = h.send_request(POWER_SWITCH_POWERON, entity='entity')
                futures.wait(timeout=1)

                m.assert_called_with('http://ip/?cmd=1&p=0&s=1')

    def test_sends_http_request_with_state_0_when_receiving_poweroff_requests(self):
        with create_powerswitch_harness() as h:

            with patch('requests.get', return_value=success_response()) as m:
                futures = h.send_request(POWER_SWITCH_POWEROFF, entity='entity')
                futures.wait(timeout=1)

                m.assert_called_with('http://ip/?cmd=1&p=0&s=0')

    def test_power_state_sends_http_request_and_parses_state_from_result_and_returns_true_when_state_on(
            self):
        with create_powerswitch_harness(gude_port=1) as h:
            with patch('requests.get',
                       return_value=success_response(json={'outputs': [{'state': 1}]})) as m:
                futures = h.send_request(POWER_SWITCH_POWER_STATE, entity='entity')
                futures.wait(timeout=1)
                assert futures[0].result(timeout=1)

                m.assert_called_with('http://ip/statusjsn.js?components=1')

    def test_power_state_sends_http_request_and_parses_state_from_result_and_returns_false_when_state_off(
            self):
        with create_powerswitch_harness(gude_port=1) as h:
            with patch('requests.get',
                       return_value=success_response(json={'outputs': [{'state': 0}]})) as m:
                futures = h.send_request(POWER_SWITCH_POWER_STATE, entity='entity')
                futures.wait(timeout=1)
                assert not futures[0].result(timeout=1)

                m.assert_called_with('http://ip/statusjsn.js?components=1')
