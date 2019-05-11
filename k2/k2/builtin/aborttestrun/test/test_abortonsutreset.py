from unittest import TestCase

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2 import CRITICAL_ABORT
from k2.runner import RUNNER_ENDPOINT
from k2.sut import SUT_RESET_STARTED

from .. import ABORT_ON_UNEXPECTED_SUT_RESET
from ..abortonsutreset import AbortOnUnexpectedSutReset


class TestCriticalAbortOnUnexpectedSutReset(TestCase):

    def test_critical_abort_triggered_when_sut_reset_received_with_expected_false(self):
        with _create_harness() as harness:
            with harness.message_queue([CRITICAL_ABORT]) as q:
                harness.trigger_event(SUT_RESET_STARTED, RUNNER_ENDPOINT, data=False)
                self.assertFalse(q.empty())

    def test_critical_abort_not_triggered_when_sut_reset_received_with_expected_true(self):
        with _create_harness() as harness:
            with harness.message_queue([CRITICAL_ABORT]) as q:
                harness.trigger_event(SUT_RESET_STARTED, RUNNER_ENDPOINT, data=True)
                self.assertTrue(q.empty())


def _create_harness(enabled=True):
    config = ConfigManager()
    config.set(ABORT_ON_UNEXPECTED_SUT_RESET, enabled)
    harness = ExtensionTestHarness(
        AbortOnUnexpectedSutReset,
        config=config,
        endpoints_and_messages={
            RUNNER_ENDPOINT: [SUT_RESET_STARTED]
        })

    return harness
