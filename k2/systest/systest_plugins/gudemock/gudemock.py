import json
import logging
import re
from http.server import BaseHTTPRequestHandler

from zaf.extensions.extension import CommandExtension

from mockserver.mockserver import HttpMockServer

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@CommandExtension('gudemock')
class GudeMockExtension(object):
    pass


class GudeMock(HttpMockServer):
    """
    Mock of a Gude power switch.

    The initial states for all 8 ports are 'ON' (represented by True).
    The mock can be changed with set_states that takes a list of booleans
    and replaces the internal states or with set_error that makes the
    mock respond with 404.

    The mock will keep a realistic representation of the states so if
    a change is set by the user the state in the mock will reflect that
    in later calls.
    """

    def __init__(self):
        self.states = [True] * 8
        self.error = False
        self.block = None
        self.block_timeout = None
        self.default_sensor_value = 0
        super().__init__(self.handler())

    def handler(self):

        class GudeHandler(BaseHTTPRequestHandler):
            parent = self

            def do_GET(self):
                if self.parent.block is not None:
                    self.parent.block.wait(timeout=self.parent.block_timeout)

                if not self.parent.error:
                    routes = {
                        r'/\?cmd=1&p=(\d+)&s=(\d+).*': self.set_state,
                        r'/statusjsn\.js\?components=1[^0-9]*': self.get_states,
                        r'/statusjsn\.js\?components=81920[^0-9]*': self.get_sensor_info,
                    }
                    for route_pattern, route in routes.items():
                        match = re.match(route_pattern, self.path)
                        if match:
                            return route(*match.groups())

                self.send_response(404)
                self.end_headers()

            def set_state(self, port, state):
                self.parent.states[int(port)] = state == '1'
                self.send_response(200)
                self.end_headers()

            def get_states(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                self.wfile.write(json.dumps(self.states_data()).encode('utf-8'))

            def states_data(self):
                return {
                    'outputs': [
                        {
                            'name': 'Power Port {port}'.format(port=port),
                            'state': state,
                            'ph_state': state,
                            'twin': 0,
                            'type': 1,
                            'batch': [0, 0, 0, 0, 0],
                            'wdog': [0, 2, '0.0.0.0']
                        } for port, state in enumerate(self.parent.states, start=1)
                    ],
                    'eof':
                    1
                }

            def get_sensor_info(self):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                self.wfile.write(json.dumps(self.sensor_info_data()).encode('utf-8'))

            def sensor_info_data(self):
                num_ports = len(self.parent.states)
                sensor_fields = {
                    'name': 'Voltage',
                    'unit': 'V',
                    'decPrecision': 3
                }, {
                    'msgCfgType': 1,
                    'name': 'Current',
                    'unit': 'A',
                    'decPrecision': 3
                }, {
                    'name': 'Frequency',
                    'unit': 'Hz',
                    'decPrecision': 2
                }, {
                    'name': 'PhaseIU',
                    'unit': 'degree',
                    'decPrecision': 2
                }, {
                    'name': 'ActivePower',
                    'unit': 'W',
                    'decPrecision': 0
                }, {
                    'name': 'ReactivePower',
                    'unit': 'VAR',
                    'decPrecision': 0
                }, {
                    'name': 'ApparentPower',
                    'unit': 'VA',
                    'decPrecision': 0
                }, {
                    'name': 'Powerfactor',
                    'unit': '',
                    'decPrecision': 2
                }, {
                    'name': 'AbsActEnergyNonRes',
                    'unit': 'kWh',
                    'decPrecision': 3
                }, {
                    'name': 'AbsReactEnergyNonRes',
                    'unit': 'kVARh',
                    'decPrecision': 3
                }, {
                    'name': 'AbsActEnergyRes',
                    'unit': 'kWh',
                    'decPrecision': 3
                }, {
                    'name': 'AbsReactEnergyRes',
                    'unit': 'kVARh',
                    'decPrecision': 3
                }, {
                    'name': 'RelativeTime',
                    'unit': 's',
                    'decPrecision': 0
                }, {
                    'name': 'FwdActEnergyNonRes',
                    'unit': 'kWh',
                    'decPrecision': 3
                }, {
                    'name': 'FwdReactEnergyNonRes',
                    'unit': 'kVARh',
                    'decPrecision': 3
                }, {
                    'name': 'FwdActEnergyRes',
                    'unit': 'kWh',
                    'decPrecision': 3
                }, {
                    'name': 'FwdReactEnergyRes',
                    'unit': 'kVARh',
                    'decPrecision': 3
                }, {
                    'name': 'RevActEnergyNonRes',
                    'unit': 'kWh',
                    'decPrecision': 3
                }, {
                    'name': 'RevReactEnergyNonRes',
                    'unit': 'kVARh',
                    'decPrecision': 3
                }, {
                    'name': 'RevActEnergyRes',
                    'unit': 'kWh',
                    'decPrecision': 3
                }, {
                    'name': 'RevReactEnergyRes',
                    'unit': 'kVARh',
                    'decPrecision': 3
                }
                return {
                    'sensor_descr': [
                        {
                            'type':
                            1,
                            'num':
                            3,
                            'options': {
                                'sumRowIndex': 2
                            },
                            'fields':
                            sensor_fields,
                            'properties': [
                                {
                                    'id': 'A',
                                    'name': 'Meter-A',
                                    'state': 0,
                                    'statistics': []
                                }, {
                                    'id': 'B',
                                    'name': 'Meter-B',
                                    'state': 0,
                                    'statistics': []
                                }, {
                                    'id': 'sum',
                                    'name': None,
                                    'state': 0,
                                    'msgCfgDisabled': 1,
                                    'statistics': []
                                }
                            ]
                        }, {
                            'type':
                            8,
                            'num':
                            12,
                            'options': {
                                'sumRowIndex': None
                            },
                            'fields':
                            sensor_fields,
                            'properties': [
                                {
                                    'id': port,
                                    'name': 'Power Port',
                                    'state': 0,
                                    'statistics': []
                                }
                                for port in [
                                    ('A' if p <= num_ports / 2 else 'B') + str(p)
                                    for p in range(1, num_ports)
                                ]
                            ]
                        }
                    ],
                    'sensor_values': [
                        {
                            'type':
                            1,
                            'num':
                            3,
                            'index':
                            0,
                            'options': {
                                'sumRowIndex': 2
                            },
                            'values': [
                                [{
                                    'v': self.parent.default_sensor_value,
                                    's': 0,
                                    'st': []
                                }] * len(sensor_fields)
                            ] * 3
                        }, {
                            'type':
                            8,
                            'num':
                            12,
                            'index':
                            0,
                            'options': {
                                'sumRowIndex': None,
                                'valid': 1
                            },
                            'values': [
                                [{
                                    'v': self.parent.default_sensor_value,
                                    's': 0,
                                    'st': []
                                }] * len(sensor_fields)
                            ] * num_ports
                        }
                    ],
                    'eof':
                    1
                }

            def log_message(self, format, *args):
                logger.debug(format, *args)

        return GudeHandler

    def set_states(self, states):
        """
        Set states to a list of booleans.

        :param states: the list of booleans
        """
        self.states = states

    def set_error(self, error=True):
        """
        If error = True then the mock will respond with 404 on all requests.

        :param error: boolean telling if the mock should return with error
        """
        self.error = error

    def set_block(self, block, timeout=None):
        """
        If set the response do_GET will block until the event is set.

        :param block: the event to block on
        """
        self.block = block
        self.block_timeout = timeout

    def set_default_sensor_value(self, value):
        """Set the default value for sensor (power, voltage, etc.)."""
        self.default_sensor_value = value
