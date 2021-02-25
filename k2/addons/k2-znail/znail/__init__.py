from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId

from k2.sut import SUT

ZNAIL_IP = ConfigOptionId('znail.ip', 'IP number to the Znail device', at=SUT)

ZNAIL_PORT = ConfigOptionId(
    'znail.port', 'Port number to connect to', option_type=int, default=80, at=SUT)

ZNAIL_TIMEOUT = ConfigOptionId(
    'znail.timeout',
    'Timeout when communicating with the Znail device, in seconds',
    option_type=int,
    default=10,
    at=SUT)

ZNAIL_CONNECTION_CHECK_ENDPOINT = EndpointId('znailcc', 'Endpoint for the Znail connection check')

ZNAIL_CONNECTION_CHECK_ENABLED = ConfigOptionId(
    'znailcc.enabled',
    'Should Znail connection check be enabled',
    at=SUT,
    option_type=bool,
    default=True)

ZNAIL_CONNECTION_CHECK_REQUIRED = ConfigOptionId(
    'znailcc.required',
    'Require Znail connection to be working',
    at=SUT,
    option_type=bool,
    default=True)


class ZnailError(Exception):
    pass
