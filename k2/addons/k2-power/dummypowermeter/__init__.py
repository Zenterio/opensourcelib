from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId

from k2.sut import SUT

DUMMY_POWER_METER_VALUE = ConfigOptionId(
    'dummypowermeter.value',
    'The power value that the dummy power meter should report',
    at=SUT,
    option_type=float,
    default=4.2)

DUMMY_POWER_METER_ENDPOINT = EndpointId('dummypowermeter', 'Endpoint for dummy power meter')
