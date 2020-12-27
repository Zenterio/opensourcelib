from enum import Enum

from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId

from k2.sut import SUT

GUDE_IP = ConfigOptionId('gude.ip', 'The gude IP for the SUT', at=SUT, default=None)

GUDE_PORT = ConfigOptionId(
    'gude.port', 'The gude port for the SUT', at=SUT, default=None, option_type=int)

GUDE_POWER_SWITCH_ENDPOINT = EndpointId(
    'gudepowerswitch', 'Endpoint for power switch when using a Gude power switch')

GUDE_POWER_METER_ENDPOINT = EndpointId(
    'gudepowermeter', 'Endpoint for power meter when using a Gude power switch')


class GudePowerState(Enum):
    OFF = 0
    ON = 1
