from unittest import TestCase
from unittest.mock import ANY

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import LocalMessageQueue

from k2 import ABORT
from k2.runner import RUNNER_ENDPOINT, TEST_CASE_FINISHED
from k2.runner.messages import TestCaseFinished
from k2.runner.testcase import Verdict

from .. import ABORT_ON_FAIL_ENABLED
from ..abortonfail import AbortOnFail


class TestAbortOnFail(TestCase):

    def test_abortonfail_pass_should_not_trigger_abort_message(self):
        assert not _is_abort_message_triggered_for_verdict(Verdict.PASSED)

    def test_abortonfail_failure_should_trigger_abort_message(self):
        assert _is_abort_message_triggered_for_verdict(Verdict.FAILED)

    def test_abortonfail_error_should_trigger_abort_message(self):
        assert _is_abort_message_triggered_for_verdict(Verdict.ERROR)

    def test_abortonfail_should_not_abort_if_disabled(self):
        with _create_harness(enabled=False) as harness:
            assert not harness.any_registered_dispatchers(TEST_CASE_FINISHED, RUNNER_ENDPOINT)


def _is_abort_message_triggered_for_verdict(verdict):
    with _create_harness() as harness:
        with LocalMessageQueue(harness.messagebus, [ABORT]) as q:
            harness.trigger_event(
                TEST_CASE_FINISHED, RUNNER_ENDPOINT, data=TestCaseFinished(ANY, ANY, ANY, verdict))
            return not q.empty()


def _create_harness(enabled=True):
    config = ConfigManager()
    config.set(ABORT_ON_FAIL_ENABLED, enabled)
    harness = ExtensionTestHarness(
        AbortOnFail, config=config, endpoints_and_messages={
            RUNNER_ENDPOINT: [TEST_CASE_FINISHED]
        })

    return harness
