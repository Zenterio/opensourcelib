from zaf.config.options import ConfigOptionId
from zaf.config.types import Flag
from zaf.messages.message import EndpointId

ABORT_ON_FAIL_ENABLED = ConfigOptionId(
    'abort.on.fail', 'Enable abort on fail addon', option_type=Flag(), default=False)

ABORT_ON_FAIL_ENDPOINT = EndpointId('abortonfailaddon', """
    Abort on fail
    """)

ABORT_ON_UNEXPECTED_SUT_RESET_ENDPOINT = EndpointId(
    'abortonunexpectedsutreset', """
    Abort on unexpected sut reset
    """)

ABORT_ON_UNEXPECTED_SUT_RESET = ConfigOptionId(
    'abort.on.unexpected.sut.reset',
    'Abort a test run when an unexpected sut reset occurs.',
    option_type=Flag(),
    default=False)
