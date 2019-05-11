from zaf.config.options import ConfigOptionId
from zaf.config.types import ConfigChoice
from zaf.messages.message import EndpointId, MessageId

from k2.sut import SUT

K2_POWER_METER_COMPONENT = 'PowerMeter'
POWER_METER_TIMEOUT = 15

AVAILABLE_POWER_METERS = ConfigOptionId(
    'powermeter.available', 'A collection of all availabe power meter options', multiple=True)

POWER_METER = ConfigOptionId(
    'powermeter',
    'The type of the power meter',
    at=SUT,
    option_type=ConfigChoice(AVAILABLE_POWER_METERS))

POWER_METER_CONNECTION_CHECK_ENDPOINT = EndpointId(
    'powermetercc', 'Endpoint for power meter connection check')

POWER_METER_CONNECTION_CHECK_ENABLED = ConfigOptionId(
    'powermetercc.enabled',
    'Should powermeter connection check be enabled',
    at=SUT,
    option_type=bool,
    default=True)

POWER_METER_CONNECTION_CHECK_REQUIRED = ConfigOptionId(
    'powermetercc.required',
    'Require powermeter connection to be working',
    at=SUT,
    option_type=bool,
    default=True)

POWER_METER_POWER = MessageId(
    'POWER_METER_POWER', """\
    Check current power consumption

    response: True/False
    exception if something failed
    """)
