from zaf.config.options import ConfigOptionId
from zaf.config.types import ConfigChoice
from zaf.messages.message import EndpointId, MessageId

from k2.sut import SUT

K2_POWER_COMPONENT = 'PowerSwitch'
POWER_SWITCH_TIMEOUT = 15

AVAILABLE_POWER_SWITCHES = ConfigOptionId(
    'powerswitch.available', 'A collection of all availabe powerswitch options', multiple=True)

POWER_SWITCH = ConfigOptionId(
    'powerswitch',
    'The type of the power switch',
    at=SUT,
    option_type=ConfigChoice(AVAILABLE_POWER_SWITCHES))

POWER_SWITCH_CONNECTION_CHECK_ENDPOINT = EndpointId(
    'powerswitchcc', 'Endpoint for power switch connection check')

POWER_SWITCH_CONNECTION_CHECK_ENABLED = ConfigOptionId(
    'powerswitchcc.enabled',
    'Should powerswitch connection check be enabled',
    at=SUT,
    option_type=bool,
    default=True)

POWER_SWITCH_CONNECTION_CHECK_REQUIRED = ConfigOptionId(
    'powerswitchcc.required',
    'Require powerswitch connection to be working',
    at=SUT,
    option_type=bool,
    default=True)

POWER_SWITCH_POWERON = MessageId(
    'POWER_SWITCH_POWERON', """\
    Makes sure that the power is on.

    exception if something failed
    """)

POWER_SWITCH_POWEROFF = MessageId(
    'POWER_SWITCH_POWEROFF', """\
    Makes sure that the power is off.

    exception if something failed
    """)

POWER_SWITCH_POWER_STATE = MessageId(
    'POWER_SWITCH_POWER_STATUS', """\
    Check if the power is on

    response: True/False
    exception if something failed
    """)
