from unittest import TestCase

from k2.cmd.run import UNINITIALIZE_SUT
from k2.sut import SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED
from sutevents import IS_SUT_RESET_EXPECTED

from .. import SUTEVENTSTIME_ENDPOINT
from .utils import MOCK_ENDPOINT, create_time_harness


class TestSutEventsTimeExtension(TestCase):

    def test_extension_can_be_set_up(self):
        with create_time_harness():
            pass

    def test_expected_reset(self):
        with create_time_harness() as harness:
            self.assertFalse(harness.extension.sut_reset_expected)
            harness.send_request(
                SUT_RESET_EXPECTED, SUTEVENTSTIME_ENDPOINT, entity='entity').wait()[0].result()
            self.assertTrue(harness.extension.sut_reset_expected)
            harness.send_request(
                SUT_RESET_NOT_EXPECTED, SUTEVENTSTIME_ENDPOINT, entity='entity').wait()[0].result()
            self.assertFalse(harness.extension.sut_reset_expected)

    def test_reset_timer_is_cancelled_on_sut_uninitialization(self):
        with create_time_harness() as harness:
            harness.send_request(
                SUT_RESET_EXPECTED, SUTEVENTSTIME_ENDPOINT, entity='entity').wait()[0].result()
            harness.send_request(
                UNINITIALIZE_SUT, MOCK_ENDPOINT, entity='entity').wait()[0].result()
            self.assertFalse(harness.extension._timer.is_started)

    def test_additional_sut_reset_expected_restarts_the_timer(self):
        with create_time_harness() as harness:
            harness.send_request(
                SUT_RESET_EXPECTED, SUTEVENTSTIME_ENDPOINT, entity='entity').wait()[0].result()
            self.assertTrue(harness.extension._timer.is_started)
            harness.send_request(
                SUT_RESET_EXPECTED, SUTEVENTSTIME_ENDPOINT, entity='entity').wait()[0].result()
            self.assertTrue(harness.extension._timer.is_started)

    def test_is_sut_reset_expected_returns_current_status(self):
        with create_time_harness() as harness:
            self.assertFalse(
                harness.send_request(
                    IS_SUT_RESET_EXPECTED, SUTEVENTSTIME_ENDPOINT,
                    entity='entity').wait()[0].result())
            harness.extension.sut_reset_expected = True

            self.assertFalse(
                harness.send_request(SUT_RESET_EXPECTED, SUTEVENTSTIME_ENDPOINT,
                                     entity='entity').wait()[0].result())
