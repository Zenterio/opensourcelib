from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId, MessageId

from k2.sut import SUT

SUTEVENTSLOG_ENDPOINT = EndpointId('suteventslog', 'Endpoint for the log based SUT events')
SUTEVENTSTIME_ENDPOINT = EndpointId('suteventstime', 'Endpoint for the time based SUT events')
SUTEVENTSCOMPONENT_ENDPOINT = EndpointId(
    'sutevents', 'Endpoint for the SUT events component extension')

LOG_LINE_RECEIVED = MessageId(
    'LOG_LINE_RECEIVED', """\
    An event that is sent for each line on the serial port
    """)

IS_SUT_RESET_EXPECTED = MessageId(
    'IS_SUT_RESET_EXPECTED', """\
    Request to check if sut reset is expected.
    """)

SUT_RESET_STARTED_PATTERN = ConfigOptionId(
    'resetstarted.pattern',
    'Pattern that matches logline that indicates that the SUT has started reset',
    at=SUT)

SUT_RESET_DONE_PATTERN = ConfigOptionId(
    'resetdone.pattern',
    'Pattern that matches logline that indicates that the SUT reset is complete',
    at=SUT)

SUT_RESET_DONE_DELAY = ConfigOptionId(
    'resetdone.delay',
    'Amount of seconds to wait after seeing pattern before sending event',
    at=SUT,
    option_type=float,
    default=0.0)
