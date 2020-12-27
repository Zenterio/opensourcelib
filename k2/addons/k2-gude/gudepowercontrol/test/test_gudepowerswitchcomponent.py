from unittest import TestCase
from unittest.mock import call, patch

from ..gudepowerswitch import GUDE_POWER_SWITCH_ENDPOINT, PowerSwitch
from .utils import create_powerswitch_harness, success_response


class TestGudePowerSwitchComponent(TestCase):

    def test_power_on_on_component_result_in_http_request(self):
        with create_powerswitch_harness() as harness:
            with patch('requests.get', return_value=success_response()) as m:
                power_switch = PowerSwitch(harness.messagebus, 'entity', GUDE_POWER_SWITCH_ENDPOINT)
                power_switch.on()
                m.assert_called_with('http://ip/?cmd=1&p=0&s=1')

    def test_power_off_on_component_result_in_http_request(self):
        with create_powerswitch_harness() as harness:
            with patch('requests.get', return_value=success_response()) as m:
                power_switch = PowerSwitch(harness.messagebus, 'entity', GUDE_POWER_SWITCH_ENDPOINT)
                power_switch.off()
                m.assert_called_with('http://ip/?cmd=1&p=0&s=0')

    def test_power_state_on_component_result_in_http_request(self):
        with create_powerswitch_harness(gude_port=1) as harness:
            with patch('requests.get',
                       return_value=success_response(json={'outputs': [{'state': 1}]})) as m:
                power_switch = PowerSwitch(harness.messagebus, 'entity', GUDE_POWER_SWITCH_ENDPOINT)
                assert power_switch.state()
                m.assert_called_with('http://ip/statusjsn.js?components=1')

    def test_off_then_on(self):
        with create_powerswitch_harness(gude_port=1) as harness:
            with patch('requests.get', return_value=success_response(json={'outputs': [{'state': 1}]})) as m, \
                    patch('time.sleep'):
                power_switch = PowerSwitch(harness.messagebus, 'entity', GUDE_POWER_SWITCH_ENDPOINT)
                power_switch.off_then_on()
                m.assert_has_calls(
                    [
                        call('http://ip/statusjsn.js?components=1'),
                        call('http://ip/?cmd=1&p=1&s=0'),
                        call('http://ip/?cmd=1&p=1&s=1')
                    ])
