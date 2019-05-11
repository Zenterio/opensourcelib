from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId, MessageId

from k2.sut import SUT

CONNECTIONCHECK_ENDPOINT = EndpointId(
    'connectioncheck', 'Endpoint for the connection check messages')

CONNECTIONCHECK_RUN_CHECK = MessageId(
    'CONNECTIONCHECK_RUN_CHECK', """\
    Tells subscribers to the message to run their checks and return the result
    as a ConnectionCheckResult.
    """)

CONNECTIONCHECK_RUN_CHECKS = MessageId(
    'CONNECTIONCHECK_RUN_CHECKS', """\
    Send to connectioncheck to trigger all connection checks.
    Raises exception if any of the required checks fail.
    """)

CONNECTIONCHECK_ENABLED = ConfigOptionId(
    'connectioncheck.enabled',
    'Enable the connection check',
    option_type=bool,
    default=True,
    at=SUT)

CONNECTIONCHECK_SHOULD_RECOVER = ConfigOptionId(
    'connectioncheck.should.recover',
    'Attempt to recover the SUT on failed connection check',
    option_type=bool,
    default=True,
    at=SUT)
