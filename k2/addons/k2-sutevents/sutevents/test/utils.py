from unittest.mock import Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.message import EndpointId

from k2.cmd.run import UNINITIALIZE_SUT
from k2.sut import SUT, SUT_RESET_DONE, SUT_RESET_DONE_TIMEOUT, SUT_RESET_EXPECTED, \
    SUT_RESET_NOT_EXPECTED
from sutevents import LOG_LINE_RECEIVED, SUT_RESET_DONE_DELAY, SUT_RESET_DONE_PATTERN, \
    SUT_RESET_STARTED_PATTERN
from sutevents.components import SutEvents, SutEventsComponentExtension
from sutevents.suteventslog import SutEventsLogExtension
from sutevents.suteventstime import SutEventsTimeExtension
from zserial import SERIAL_ENABLED

MOCK_ENDPOINT = EndpointId('mock', 'Mock endpoint')


def create_log_harness(
        sut=['entity'],
        reset_started_pattern='START_PATTERN',
        reset_done_pattern='DONE_PATTERN',
        reset_done_delay=0):

    config = ConfigManager()
    entity = sut[0]
    config.set(SUT, sut)
    config.set(SUT_RESET_DONE_TIMEOUT, 1, entity=entity)
    config.set(SERIAL_ENABLED, True, entity=entity)
    config.set(SUT_RESET_STARTED_PATTERN, reset_started_pattern, entity=entity)
    config.set(SUT_RESET_DONE_PATTERN, reset_done_pattern, entity=entity)
    config.set(SUT_RESET_DONE_DELAY, reset_done_delay, entity=entity)

    return ExtensionTestHarness(
        SutEventsLogExtension,
        endpoints_and_messages={
            MOCK_ENDPOINT:
            [LOG_LINE_RECEIVED, SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED, UNINITIALIZE_SUT],
        },
        config=config)


def create_time_harness(sut=['entity']):
    config = ConfigManager()
    entity = sut[0]
    config.set(SUT, sut)
    config.set(SUT_RESET_DONE_TIMEOUT, 1, entity=entity)
    config.set(SERIAL_ENABLED, False, entity=entity)
    config.set(SUT_RESET_STARTED_PATTERN, None, entity=entity)
    config.set(SUT_RESET_DONE_PATTERN, None, entity=entity)

    return ExtensionTestHarness(
        SutEventsTimeExtension,
        endpoints_and_messages={
            MOCK_ENDPOINT: [SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED, UNINITIALIZE_SUT],
        },
        config=config)


def create_component_harness(sut=['entity']):
    component_sut = Mock()
    component_sut.entity = sut[0]

    return ExtensionTestHarness(
        SutEventsComponentExtension,
        endpoints_and_messages={
            MOCK_ENDPOINT: [LOG_LINE_RECEIVED, SUT_RESET_DONE],
        },
        components=[ComponentMock(name='Sut', mock=component_sut), SutEvents])
