from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId, MessageId

MULTI_RUNNER_ENABLED = ConfigOptionId(
    'multirunner.enabled', 'Should multi-runner be enabled', option_type=bool, default=True)

MULTI_RUNNER_ENDPOINT = EndpointId('multirunner', 'stub')

TEST_SUBRUN = MessageId('TEST_SUBRUN', 'stub')
