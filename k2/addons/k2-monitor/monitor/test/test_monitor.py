from unittest import TestCase

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import LocalMessageQueue

from k2 import ABORT, CRITICAL_ABORT, K2_APPLICATION_ENDPOINT
from k2.runner import RUNNER_ENDPOINT, TEST_RUN_FINISHED, TEST_RUN_STARTED
from k2.sut import SUT, SUT_RESET_DONE, SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED, \
    SUT_RESET_STARTED

from ..monitor import MONITOR_ENABLED, MONITOR_ENDPOINT, PERFORM_MEASUREMENT, Monitor


class TestMonitor(TestCase):

    def test_can_be_enabled(self):
        with _create_harness(enabled=True) as harness:
            assert harness.any_registered_dispatchers(TEST_RUN_STARTED, RUNNER_ENDPOINT)

    def test_starts_sending_perform_measurement_requests_when_the_test_run_start(self):
        with _create_harness() as harness:
            with LocalMessageQueue(harness.messagebus, message_ids=[PERFORM_MEASUREMENT],
                                   endpoint_ids=[MONITOR_ENDPOINT], entities=['mysut']) as queue:
                initial_timer = harness.extension._timer
                harness.messagebus.trigger_event(TEST_RUN_STARTED, RUNNER_ENDPOINT)
                queue.get(timeout=1)
                assert harness.extension._timer is not initial_timer


def _create_harness(enabled=True):
    config = ConfigManager()
    entity = 'mysut'
    config.set(SUT, [entity])
    config.set(MONITOR_ENABLED, enabled, entity=entity)

    return ExtensionTestHarness(
        Monitor,
        config=config,
        endpoints_and_messages={
            RUNNER_ENDPOINT: [TEST_RUN_STARTED, TEST_RUN_FINISHED],
            K2_APPLICATION_ENDPOINT: [
                ABORT, CRITICAL_ABORT, SUT_RESET_STARTED, SUT_RESET_DONE, SUT_RESET_EXPECTED,
                SUT_RESET_NOT_EXPECTED
            ],
        },
    )
