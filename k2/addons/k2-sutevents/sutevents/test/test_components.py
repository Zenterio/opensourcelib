import unittest
from unittest.mock import MagicMock, Mock

from zaf.component.factory import Factory
from zaf.component.manager import ComponentManager
from zaf.messages.messagebus import MessageBus

from k2.sut import SUT_RESET_DONE, SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED
from k2.sut.log import SUT_LOG_SOURCES
from sutevents import LOG_LINE_RECEIVED, SUTEVENTSCOMPONENT_ENDPOINT
from sutevents.components import NoMatchingLogLine, SutEventTimeout

from ..components import SutEvents
from .utils import MOCK_ENDPOINT, create_component_harness

TIMEOUT = 5


def config_get_log_sources(config_option, entity):
    return ['log-entity'] if config_option == SUT_LOG_SOURCES and entity == 'entity' else None


class TestSutEventsComponentsExtension(unittest.TestCase):

    def test_extension_can_be_setup(self):
        with create_component_harness():
            pass


class TestWaitForLine(unittest.TestCase):

    def setUp(self):
        self.messagebus = MessageBus(Factory(ComponentManager({})))
        self.endpoint = MOCK_ENDPOINT
        self.sut = Mock()
        self.sut.entity = 'entity'
        self.config = Mock()
        self.config.get = MagicMock(side_effect=config_get_log_sources)
        self.messagebus.define_endpoints_and_messages({self.endpoint: [LOG_LINE_RECEIVED]})

    def test_wait_for_line_times_out(self):
        sut_events = SutEvents(self.messagebus, self.config, self.sut)
        with sut_events.wait_for_log_line(r'not matching') as lines:
            self.messagebus.trigger_event(
                LOG_LINE_RECEIVED, self.endpoint, entity='log-entity', data='line')
            with self.assertRaises(NoMatchingLogLine):
                lines.get(timeout=0)

    def test_wait_for_line_matches_first_line(self):
        [match] = list(self.wait_for_lines(r'li\w+', ['line'], 1))
        self.assertEqual(match.string, 'line')

    def test_wait_for_line_matches_some_lines(self):
        [match1, match2] = list(
            self.wait_for_lines(r'match\d+', ['match1', 'no match', 'match2', 'no match'], 2))
        self.assertEqual(match1.string, 'match1')
        self.assertEqual(match2.string, 'match2')

    def test_wait_for_line_matches_with_match_groups(self):
        [match] = list(self.wait_for_lines(r'(\S+) (\S+)', ['first second'], 1))
        self.assertEqual(match.group(1), 'first')
        self.assertEqual(match.group(2), 'second')

    def test_wait_for_line_matches_with_named_match_groups(self):
        [match] = list(self.wait_for_lines(r'(?P<first>\S+) (?P<second>\S+)', ['first second'], 1))
        self.assertEqual(match.group('first'), 'first')
        self.assertEqual(match.group('second'), 'second')

    def test_wait_for_line_matches_when_match_is_not_at_start_of_line(self):
        [match] = list(self.wait_for_lines(r'(?P<second>second)', ['first second'], 1))
        self.assertEqual(match.string, 'first second')
        self.assertEqual(match.group('second'), 'second')

    def wait_for_lines(self, log_line_regex, lines, expected_matches):
        sut_events = SutEvents(self.messagebus, self.config, self.sut)
        with sut_events.wait_for_log_line(log_line_regex) as received_lines:
            for line in lines:
                self.messagebus.trigger_event(
                    LOG_LINE_RECEIVED, self.endpoint, entity='log-entity', data=line)

            return [received_lines.get(timeout=0) for _ in range(0, expected_matches)]

    def test_get_all_lines(self):
        lines = ['first A', 'second B', 'third A', 'fourth B']
        regex = r'A'
        matching_lines = ['first A', 'third A']
        sut_events = SutEvents(self.messagebus, self.config, self.sut)
        with sut_events.wait_for_log_line(regex) as queue:
            for line in lines:
                self.messagebus.trigger_event(
                    LOG_LINE_RECEIVED, self.endpoint, entity='log-entity', data=line)
            self.messagebus.wait_for_not_active()
            matches = queue.get_all()
        strings = [match.string for match in matches]
        self.assertEqual(strings, matching_lines)


class TestExpectReset(unittest.TestCase):

    def test_expect_reset_sends_messages(self):
        sut = Mock()
        sut.entity = 'my_entity'
        config = Mock()

        with create_component_harness() as harness, \
                harness.message_queue([SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED], entities=['my_entity']) as queue:

            sutevents = SutEvents(harness.messagebus, config, sut)
            with sutevents.expect_reset():
                message = queue.get(TIMEOUT)
                self.assertEqual(message.message_id, SUT_RESET_EXPECTED)
            message = queue.get(TIMEOUT)
            self.assertEqual(message.message_id, SUT_RESET_NOT_EXPECTED)


class TestAwaitSutMessage(unittest.TestCase):

    def setUp(self):
        self.messagebus = MessageBus(Factory(ComponentManager({})))
        self.sut = MagicMock()
        self.sut.entity = 'entity1'
        config = Mock()

        self.messagebus.define_endpoints_and_messages(
            {
                MOCK_ENDPOINT: [SUT_RESET_EXPECTED],
                SUTEVENTSCOMPONENT_ENDPOINT: [SUT_RESET_EXPECTED, SUT_RESET_DONE]
            })
        self.sut_events = SutEvents(self.messagebus, config, self.sut)

    def test_that_await_message_returns_future_with_message(self):
        with self.sut_events.await_sut_message(SUT_RESET_EXPECTED, timeout=1) as future:
            self.messagebus.trigger_event(SUT_RESET_EXPECTED, MOCK_ENDPOINT, entity=self.sut.entity)
        message = future.result(timeout=0)
        self.assertEqual(message.message_id, SUT_RESET_EXPECTED)

    def test_that_await_message_blocks_raises_exception_when_timing_out(self):
        with self.assertRaises(SutEventTimeout):
            with self.sut_events.await_sut_message(SUT_RESET_EXPECTED, timeout=0):
                pass

    def test_that_await_reset_done_returns_future_with_reset_done_message(self):
        with self.sut_events.await_sut_reset_done(timeout=1) as future:
            self.messagebus.trigger_event(
                SUT_RESET_DONE, SUTEVENTSCOMPONENT_ENDPOINT, entity=self.sut.entity)
        message = future.result(timeout=0)
        self.assertEqual(message.message_id, SUT_RESET_DONE)
