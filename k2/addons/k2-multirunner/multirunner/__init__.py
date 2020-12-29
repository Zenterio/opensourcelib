from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId, MessageId

MULTI_RUNNER_ENDPOINT = EndpointId('customrunner', 'Endpoint for the custom runner')

MULTI_RUNNER_ENABLED = ConfigOptionId(
    'multi.runner.enabled', (
        'Enable the custom runner. '
        'The normal test runner needs to be disabled for this to work as expected.'),
    option_type=bool,
    default=False)

TEST_SUBRUN = MessageId(
    'TEST_SUBRUN', """\
    Triggered when the test sub-run is started.

    data: None
    """)
