from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId

from k2.sut import SUT

SISPM_DEVICE = ConfigOptionId(
    'sispmpowerswitch.device', "Which device 'n' to talk to", at=SUT, option_type=int, default=0)

SISPM_OUTLET = ConfigOptionId(
    'sispmpowerswitch.outlet', 'Which outlet to use', at=SUT, option_type=int, default=1)

SISPM_POWER_SWITCH_ENDPOINT = EndpointId(
    'sispmpowerswitch', 'Endpoint for Silver Shield PM USB relay')
