from unittest import TestCase
from unittest.mock import patch

from zaf.config import MissingConditionalConfigOption

from powermeter import POWER_METER_POWER

from ..gudepowermeter import GUDE_INDIVIDUAL_PORT_MEASUREMENTS, GudePowerMeterError
from .utils import create_powermeter_harness, create_valid_power_json_response, error_response, \
    success_response


class TestGudePowerMeterExtension(TestCase):

    def test_not_enabled_if_powermeter_config_is_not_gude(self):
        with create_powermeter_harness(power_meter='notgude') as harness:
            assert not harness.extension.is_active

    def test_enabled_if_powermeter_config_is_gude(self):
        with create_powermeter_harness() as harness:
            assert harness.extension.is_active

    def test_initialize_raises_exception_if_ip_or_port_is_missing(self):
        with self.assertRaises(MissingConditionalConfigOption):
            harness = create_powermeter_harness(gude_ip=None)
            harness.__enter__()

        with self.assertRaises(MissingConditionalConfigOption):
            harness = create_powermeter_harness(gude_port=None)
            harness.__enter__()

    def test_power_raises_if_no_sensor_info(self):
        with self.assertRaises(GudePowerMeterError):
            with patch('requests.get', return_value=error_response):
                with create_powermeter_harness() as h:
                    futures = h.send_request(POWER_METER_POWER, entity='entity')
                    futures.wait(timeout=1)
                    futures[0].result(timeout=1)

    def test_power_raises_if_missing_individual_port_sensor_descriptions(self):
        json = create_valid_power_json_response(port=1, value=42)
        json['sensor_descr'][0]['type'] = GUDE_INDIVIDUAL_PORT_MEASUREMENTS + 1
        with self.assertRaises(GudePowerMeterError):
            with patch('requests.get', return_value=success_response(json=json)):
                with create_powermeter_harness() as h:
                    futures = h.send_request(POWER_METER_POWER, entity='entity')
                    futures.wait(timeout=1)
                    futures[0].result(timeout=1)

    def test_power_raises_if_missing_individual_port_sensor_values(self):
        json = create_valid_power_json_response(port=1, value=42)
        json['sensor_values'][0]['type'] = GUDE_INDIVIDUAL_PORT_MEASUREMENTS + 1
        with self.assertRaises(GudePowerMeterError):
            with patch('requests.get', return_value=success_response(json=json)):
                with create_powermeter_harness() as h:
                    futures = h.send_request(POWER_METER_POWER, entity='entity')
                    futures.wait(timeout=1)
                    futures[0].result(timeout=1)

    def test_power_raises_if_no_sensor_descriptions(self):
        valid_json = create_valid_power_json_response(port=1, value=42)
        json = {'sensor_values': valid_json['sensor_values']}
        with self.assertRaises(GudePowerMeterError):
            with patch('requests.get', return_value=success_response(json=json)):
                with create_powermeter_harness() as h:
                    futures = h.send_request(POWER_METER_POWER, entity='entity')
                    futures.wait(timeout=1)
                    futures[0].result(timeout=1)

    def test_power_raises_if_no_sensor_values(self):
        valid_json = create_valid_power_json_response(port=1, value=42)
        json = {'sensor_descr': valid_json['sensor_descr']}
        with self.assertRaises(GudePowerMeterError):
            with patch('requests.get', return_value=success_response(json=json)):
                with create_powermeter_harness() as h:
                    futures = h.send_request(POWER_METER_POWER, entity='entity')
                    futures.wait(timeout=1)
                    futures[0].result(timeout=1)

    def test_correct_power_value(self):
        port = 1
        valid_json = create_valid_power_json_response(port=port, value=42)
        with patch('requests.get', return_value=success_response(json=valid_json)):
            with create_powermeter_harness(gude_port=port) as h:
                futures = h.send_request(POWER_METER_POWER, entity='entity')
                futures.wait(timeout=1)
                assert futures[0].result(timeout=1) == 42

    def test_use_of_wrong_port(self):
        port = 1
        valid_json = create_valid_power_json_response(port=port, value=42)
        with patch('requests.get', return_value=success_response(json=valid_json)):
            with create_powermeter_harness(gude_port=port + 1) as h:
                futures = h.send_request(POWER_METER_POWER, entity='entity')
                futures.wait(timeout=1)
                assert futures[0].result(timeout=1) != 42
