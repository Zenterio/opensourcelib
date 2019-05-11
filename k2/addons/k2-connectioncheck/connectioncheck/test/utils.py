from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import CallbackDispatcher
from zaf.messages.message import EndpointId

from k2.cmd.run import POST_INITIALIZE_SUT, RUN_COMMAND_ENDPOINT
from k2.sut import SUT, SUT_RECOVERY_PERFORM

from .. import CONNECTIONCHECK_ENABLED, CONNECTIONCHECK_RUN_CHECK, CONNECTIONCHECK_SHOULD_RECOVER
from ..connectioncheck import ConnectionCheck, ConnectionCheckResult

MOCK_CONNECTION_CHECK_ENDPOINT = EndpointId('mockcc', 'Mock connection check')
MOCK_SUT_RECOVER = EndpointId('mocksr', 'Mock sut recover')


def create_harness(enabled=True, should_recover=True, sut=['entity']):
    config = ConfigManager()
    entity = sut[0]
    config.set(SUT, sut)
    config.set(CONNECTIONCHECK_ENABLED, enabled, entity=entity)
    config.set(CONNECTIONCHECK_SHOULD_RECOVER, should_recover, entity=entity)

    return ExtensionTestHarness(
        ConnectionCheck,
        endpoints_and_messages={
            RUN_COMMAND_ENDPOINT: [POST_INITIALIZE_SUT],
            MOCK_CONNECTION_CHECK_ENDPOINT: [CONNECTIONCHECK_RUN_CHECK],
            MOCK_SUT_RECOVER: [SUT_RECOVERY_PERFORM],
        },
        config=config)


class MockConnectionCheck(object):

    def __init__(self, messagebus, success, required, entity):
        self.messagebus = messagebus
        self.success = success
        self.required = required
        self.entity = entity
        self.dispatcher = None

        self.executed = False

    def __enter__(self):
        self.dispatcher = CallbackDispatcher(self.messagebus, self.return_result)
        self.dispatcher.register(
            [CONNECTIONCHECK_RUN_CHECK], [MOCK_CONNECTION_CHECK_ENDPOINT], [self.entity])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.dispatcher:
            self.dispatcher.destroy()

    def return_result(self, message):
        self.executed = True
        return ConnectionCheckResult('mockcc', self.success, self.required, 'message')
