from unittest.mock import Mock

from requests import HTTPError
from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2.sut import SUT
from powermeter import AVAILABLE_POWER_METERS, POWER_METER
from powerswitch import AVAILABLE_POWER_SWITCHES

from ..gudepowermeter import GUDE_INDIVIDUAL_PORT_MEASUREMENTS, GudePowerMeterExtension
from ..gudepowerswitch import GUDE_IP, GUDE_PORT, POWER_SWITCH, GudePowerSwitchExtension


def success_response(json=None):
    mock = Mock
    mock.status_code = 200
    mock.json = Mock(side_effect=lambda: json)
    mock.raise_for_status = Mock(side_effect=lambda: None)
    return mock


def error_response():
    mock = Mock
    mock.status_code = 400

    def raise_http_error():
        raise HTTPError()

    mock.raise_for_status = Mock(side_effect=raise_http_error)
    return mock


def create_powerswitch_harness(sut=['entity'], gude_port=0, gude_ip='ip', power_switch='gude'):
    config = ConfigManager()
    entity = sut[0]
    config.set(SUT, sut)
    config.set(AVAILABLE_POWER_SWITCHES, ['gude', 'notgude'])
    config.set(POWER_SWITCH, power_switch, entity=entity)
    config.set(GUDE_PORT, gude_port, entity=entity)
    config.set(GUDE_IP, gude_ip, entity=entity)

    return ExtensionTestHarness(GudePowerSwitchExtension, config=config)


def create_powermeter_harness(sut=['entity'], gude_port=0, gude_ip='ip', power_meter='gude'):
    config = ConfigManager()
    entity = sut[0]
    config.set(SUT, sut)
    config.set(AVAILABLE_POWER_METERS, ['gude', 'notgude'])
    config.set(POWER_METER, power_meter, entity=entity)
    config.set(GUDE_PORT, gude_port, entity=entity)
    config.set(GUDE_IP, gude_ip, entity=entity)

    return ExtensionTestHarness(GudePowerMeterExtension, config=config)


def create_valid_power_json_response(port, value, num_ports=12):
    json = {}
    json['sensor_descr'] = [
        {
            'type': GUDE_INDIVIDUAL_PORT_MEASUREMENTS,
            'fields': [{
                'name': 'ActivePower',
                'unit': 'W'
            }]
        }
    ]
    json['sensor_values'] = [
        {
            'type': GUDE_INDIVIDUAL_PORT_MEASUREMENTS,
            'values': [[{
                'v': value if p + 1 == port else 0
            }] for p in range(num_ports)]
        }
    ]
    return json


def create_stb(entity='entity'):
    stb = Mock()
    stb.entity = entity
    return stb
