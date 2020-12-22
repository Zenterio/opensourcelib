from queue import Empty
from unittest import TestCase
from unittest.mock import MagicMock

from k2.cmd.run import UNINITIALIZE_SUT
from k2.sut import SUT_RESET_DONE, SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED, SUT_RESET_STARTED

from .. import LOG_LINE_RECEIVED, SUTEVENTSLOG_ENDPOINT
from .utils import MOCK_ENDPOINT, create_log_harness


class TestSutEventsLogExtension(TestCase):

    def test_extension_can_be_set_up(self):
        with create_log_harness():
            pass

    def test_expected_reset(self):
        with create_log_harness() as harness:
            self.assertFalse(harness.extension.sut_reset_expected)
            harness.send_request(
                SUT_RESET_EXPECTED, SUTEVENTSLOG_ENDPOINT, entity='entity').wait()[0].result()
            self.assertTrue(harness.extension.sut_reset_expected)
            harness.send_request(
                SUT_RESET_NOT_EXPECTED, SUTEVENTSLOG_ENDPOINT, entity='entity').wait()[0].result()
            self.assertFalse(harness.extension.sut_reset_expected)

    def test_detects_reset_started(self):
        with create_log_harness(reset_started_pattern='STARTED') as harness:
            with harness.message_queue([SUT_RESET_STARTED], entities=['entity']) as queue:
                harness.trigger_event(
                    LOG_LINE_RECEIVED, MOCK_ENDPOINT, entity='entity', data='Not a match')
                harness.trigger_event(
                    LOG_LINE_RECEIVED, MOCK_ENDPOINT, entity='entity', data='STARTED')
                self.assertEqual(queue.get(timeout=2).message_id, SUT_RESET_STARTED)
                with self.assertRaises(Empty):
                    queue.get_nowait()

    def test_detect_reset_done(self):
        with create_log_harness(reset_done_pattern='DONE') as harness:
            with harness.message_queue([SUT_RESET_DONE], entities=['entity']) as queue:
                harness.trigger_event(
                    LOG_LINE_RECEIVED, MOCK_ENDPOINT, entity='entity', data='Not a match')
                harness.trigger_event(
                    LOG_LINE_RECEIVED, MOCK_ENDPOINT, entity='entity', data='DONE')
                self.assertEqual(queue.get(timeout=2).message_id, SUT_RESET_DONE)
                with self.assertRaises(Empty):
                    queue.get_nowait()

    def test_trigger_reset_done_with_delay(self):
        with create_log_harness(reset_done_pattern='DONE', reset_done_delay=0.01) as harness:
            with harness.message_queue([SUT_RESET_DONE], entities=['entity']) as queue:
                harness.trigger_event(
                    LOG_LINE_RECEIVED, MOCK_ENDPOINT, entity='entity', data='DONE')
                self.assertEqual(queue.get(timeout=2).message_id, SUT_RESET_DONE)
                self.assertEqual(harness.extension.pattern_handlers['DONE'].interval, 0.01)

    def test_triggers_are_cancelled_on_sut_uninitialization(self):
        with create_log_harness(reset_done_pattern='DONE', reset_done_delay=2) as harness:
            harness.extension.handle_line('DONE', messagebus=MagicMock())
            self.assertTrue(harness.extension.pattern_handlers['DONE'].is_started)
            harness.trigger_event(UNINITIALIZE_SUT, MOCK_ENDPOINT, entity='entity')
            self.assertFalse(harness.extension.pattern_handlers['DONE'].is_started)

    def test_triggers_are_cancelled_on_sut_reset(self):
        with create_log_harness(reset_started_pattern='STARTED', reset_done_pattern='DONE',
                                reset_done_delay=2) as harness:
            harness.extension.handle_line('DONE', messagebus=MagicMock())
            self.assertTrue(harness.extension.pattern_handlers['DONE'].is_started)
            harness.extension.handle_line('STARTED', messagebus=MagicMock())
            self.assertFalse(harness.extension.pattern_handlers['DONE'].is_started)
