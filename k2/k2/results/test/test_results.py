from unittest import TestCase

from zaf.builtin.unittest.harness import ExtensionTestHarness

from k2.cmd.run import GET_RUN_VERDICT, RUN_COMMAND_ENDPOINT
from k2.results import TEST_RESULTS_COLLECTED
from k2.runner import RUNNER_ENDPOINT
from k2.runner.messages import TEST_CASE_FINISHED, TEST_CASE_SKIPPED, TEST_CASE_STARTED, \
    TEST_RUN_FINISHED, TEST_RUN_STARTED, trigger_test_case_finished, trigger_test_case_skipped, \
    trigger_test_case_started, trigger_test_run_finished, trigger_test_run_started
from k2.runner.runner import Verdict
from k2.runner.testcase import RunnerTestCase

from ..results import TestResults


class TestTestResults(TestCase):

    @staticmethod
    def create_harness():
        harness = ExtensionTestHarness(
            TestResults,
            endpoints_and_messages={
                RUNNER_ENDPOINT: [
                    TEST_CASE_FINISHED, TEST_CASE_SKIPPED, TEST_CASE_STARTED, TEST_RUN_FINISHED,
                    TEST_RUN_STARTED, GET_RUN_VERDICT
                ],
                RUN_COMMAND_ENDPOINT: [GET_RUN_VERDICT],
            })
        return harness

    def test_create_harness(self):
        with self.create_harness():
            pass

    def test_run_with_single_test_case(self):
        tc1 = RunnerTestCase(lambda: None, name='tc1')
        tc1.verdict = Verdict.PASSED

        with self.create_harness() as harness:
            trigger_test_case_started(harness.messagebus, tc1)
            trigger_test_case_finished(harness.messagebus, tc1)

        assert len(harness.extension._test_results) == 1
        assert harness.extension._test_results[tc1.execution_id].name == 'tc1'
        assert harness.extension._test_results[tc1.execution_id].verdict == Verdict.PASSED

    def test_run_with_multiple_test_cases(self):
        tc1 = RunnerTestCase(lambda: None, name='tc1')
        tc1.verdict = Verdict.PASSED

        tc2 = RunnerTestCase(lambda: None, name='tc2')
        tc2.verdict = Verdict.FAILED

        with self.create_harness() as harness:
            trigger_test_case_started(harness.messagebus, tc1)
            trigger_test_case_finished(harness.messagebus, tc1)

            trigger_test_case_started(harness.messagebus, tc2)
            trigger_test_case_finished(harness.messagebus, tc2)

        assert len(harness.extension._test_results) == 2
        assert harness.extension._test_results[tc1.execution_id].name == 'tc1'
        assert harness.extension._test_results[tc1.execution_id].verdict == Verdict.PASSED
        assert harness.extension._test_results[tc2.execution_id].name == 'tc2'
        assert harness.extension._test_results[tc2.execution_id].verdict == Verdict.FAILED

    def test_run_with_skipped_test_case(self):
        tc1 = RunnerTestCase(lambda: None, name='tc1')
        tc1.verdict = Verdict.PASSED

        with self.create_harness() as harness:
            trigger_test_case_skipped(harness.messagebus, tc1, reason='hoppsan')

        assert len(harness.extension._test_results) == 1
        assert harness.extension._test_results[tc1.execution_id].name == 'tc1'
        assert harness.extension._test_results[tc1.execution_id].verdict == Verdict.SKIPPED

    def test_triggers_a_test_results_collected_event_when_run_is_complete(self):
        with self.create_harness() as harness:
            with harness.message_queue([TEST_RESULTS_COLLECTED]) as queue:
                trigger_test_run_started(harness.messagebus, 'tr1')
                trigger_test_run_finished(harness.messagebus, Verdict.PASSED, message='hejhopp')
                queue.get(timeout=5)

    def test_get_verdict_of_passed_run(self):
        with self.create_harness() as harness:
            trigger_test_run_started(harness.messagebus, 'tr1')
            trigger_test_run_finished(harness.messagebus, Verdict.PASSED, message='hejhopp')
            harness.messagebus.wait_for_not_active()
            futures = harness.messagebus.send_request(GET_RUN_VERDICT, RUN_COMMAND_ENDPOINT)
            assert futures[0].result() == Verdict.PASSED

    def test_get_verdict_of_failed_run(self):
        with self.create_harness() as harness:
            trigger_test_run_started(harness.messagebus, 'tr1')
            trigger_test_run_finished(harness.messagebus, Verdict.FAILED, message='hejhopp')
            harness.messagebus.wait_for_not_active()
            futures = harness.messagebus.send_request(GET_RUN_VERDICT, RUN_COMMAND_ENDPOINT)
            assert futures[0].result() == Verdict.FAILED
