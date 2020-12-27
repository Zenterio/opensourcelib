from unittest import TestCase
from unittest.mock import patch

from ..gudepowermeter import GUDE_POWER_METER_ENDPOINT, PowerMeter
from .utils import create_powermeter_harness, create_valid_power_json_response, success_response


class TestGudePowerMeterComponent(TestCase):

    def test_power_on_component_result_in_http_request(self):
        port = 1
        power = 42
        with patch('requests.get', return_value=success_response(
                json=create_valid_power_json_response(port=port, value=power))) as m:
            with create_powermeter_harness(gude_port=port) as harness:
                power_meter = PowerMeter(harness.messagebus, 'entity', GUDE_POWER_METER_ENDPOINT)
                assert power_meter.power() == power
                m.assert_called_with('http://ip/statusjsn.js?components=81920')
