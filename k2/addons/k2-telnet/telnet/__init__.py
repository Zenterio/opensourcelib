from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId

from k2.sut import SUT

TELNET_CONNECTION_CHECK_ENDPOINT = EndpointId(
    'telnetcc', 'Endpoint for the telnet connection check')

TELNET_ENABLED = ConfigOptionId(
    'telnet.enabled', 'Should telnet be enabled', at=SUT, option_type=bool, default=True)

TELNET_CONNECTION_CHECK_ENABLED = ConfigOptionId(
    'telnetcc.enabled',
    'Should telnet connection check be enabled',
    at=SUT,
    option_type=bool,
    default=True)

TELNET_CONNECTION_CHECK_REQUIRED = ConfigOptionId(
    'telnetcc.required',
    'Require telnet connection to be working',
    at=SUT,
    option_type=bool,
    default=True)

TELNET_PORT = ConfigOptionId(
    'telnet.port', 'Port to use when connecting to the SUT', at=SUT, option_type=int, default=23)

TELNET_TIMEOUT = ConfigOptionId(
    'telnet.timeout',
    'Default timeout when waiting for a command to complete',
    at=SUT,
    option_type=int,
    default=60)

TELNET_PROMPT = ConfigOptionId(
    'telnet.prompt', 'Regular expression matching the prompt of the SUT', at=SUT, default=r'.* # ')
