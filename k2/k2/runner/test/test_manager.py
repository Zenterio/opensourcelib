from unittest import TestCase
from unittest.mock import MagicMock

from zaf.builtin.unittest.harness import ExtensionTestHarness, SyncMock
from zaf.messages.dispatchers import CallbackDispatcher, LocalMessageQueue

from k2 import ABORT, CRITICAL_ABORT
from k2.cmd.run import RUN_COMMAND_ENDPOINT, TEST_RUN
from k2.runner import ABORT_TEST_CASE_REQUEST, RUNNER_ENDPOINT, TEST_RUN_FINISHED, TEST_RUN_STARTED
from k2.scheduler import SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT
from k2.sut import SUT_RESET_DONE, SUT_RESET_STARTED

from ..manager import TestRunnerManager

MOCK_ENDPOINT = MagicMock()

TIMEOUT = 5


class TestTestRunnerExtension(TestCase):

    @staticmethod
    def create_harness():
        harness = ExtensionTestHarness(
            TestRunnerManager,
            endpoints_and_messages={
                MOCK_ENDPOINT: [SUT_RESET_STARTED, SUT_RESET_DONE],
                RUN_COMMAND_ENDPOINT: [ABORT, CRITICAL_ABORT, TEST_RUN],
                SCHEDULER_ENDPOINT: [SCHEDULE_NEXT_TEST],
            })
        harness.schedule_test_case = None

        def schedule_test_case(message):
            harness.schedule_test_case = message
            return None

        scheduler_dispatcher = CallbackDispatcher(harness.messagebus, schedule_test_case)
        scheduler_dispatcher.register([SCHEDULE_NEXT_TEST], [SCHEDULER_ENDPOINT])
        return harness

    def test_trigger_test_run_started_and_finished_on_test_run(self):
        """Trigger events TEST_RUN_STARTED and TEST_RUN_FINISHED, on message TEST_RUN."""
        with self.create_harness() as harness:
            events = [TEST_RUN_STARTED, TEST_RUN_FINISHED]
            with LocalMessageQueue(harness.messagebus, events) as queue:
                harness.messagebus.trigger_event(TEST_RUN, RUN_COMMAND_ENDPOINT, data=MagicMock())
                self.assertEqual(queue.get(timeout=TIMEOUT).message_id, TEST_RUN_STARTED)
                self.assertEqual(queue.get(timeout=TIMEOUT).message_id, TEST_RUN_FINISHED)

    def test_abort_after_current_test_case_on_abort(self):
        """Abort after the current test case, on message ABORT."""
        with self.create_harness() as harness:
            runner_mock = SyncMock()
            runner_mock.abort_run_after_current_test_cases_have_completed = SyncMock()
            harness.extension._runner = runner_mock
            harness.trigger_event(ABORT, RUN_COMMAND_ENDPOINT)
            runner_mock.abort_run_after_current_test_cases_have_completed.wait_for_call(
                timeout=TIMEOUT)

    def test_abort_immediately_on_critical_abort(self):
        """Abort immediately, on message CRITICAL_ABORT."""
        with self.create_harness() as harness:
            runner_mock = SyncMock()
            runner_mock.abort_run_immediately = SyncMock()
            harness.extension._runner = runner_mock
            harness.trigger_event(CRITICAL_ABORT, RUN_COMMAND_ENDPOINT)
            runner_mock.abort_run_immediately.wait_for_call(timeout=TIMEOUT)

    def test_request_abort_test_case(self):
        with self.create_harness() as harness:
            runner_mock = MagicMock()
            harness.extension._runner = runner_mock
            harness.send_request(
                ABORT_TEST_CASE_REQUEST, RUNNER_ENDPOINT, data=MagicMock()).wait()[0].result()
            self.assertEqual(runner_mock.abort_test_case.call_count, 1)

    def test_pausing_execution_on_sut_reset_started(self):
        """Pause execution, on message SUT_RESET_STARTED."""
        with self.create_harness() as harness:
            runner_mock = SyncMock()
            runner_mock.pause_execution = SyncMock()
            entity = MagicMock()
            harness.extension._runner = runner_mock
            harness.trigger_event(SUT_RESET_STARTED, MOCK_ENDPOINT, entity=entity, data=False)
            runner_mock.pause_execution.wait_for_call(timeout=TIMEOUT)

    def test_resume_execution_on_sut_reset_done(self):
        """Resume execution, on message SUT_RESET_DONE."""
        with self.create_harness() as harness:
            runner_mock = SyncMock()
            runner_mock.resume_execution = SyncMock()
            entity = MagicMock()
            harness.extension._runner = runner_mock
            harness.extension._resetting_entities.add(entity)
            harness.trigger_event(SUT_RESET_DONE, MOCK_ENDPOINT, entity=entity, data=False)
            runner_mock.resume_execution.wait_for_call(timeout=TIMEOUT)

    def test_multiple_sut_reset_started_before_single_reset_done(self):
        """Receiving multiple SUT_RESET_STARTED before a single SUT_RESET_DONE is okay."""
        with self.create_harness() as harness:
            runner_mock = SyncMock()
            runner_mock.resume_execution = SyncMock()
            runner_mock.pause_execution = SyncMock()
            entity = MagicMock()
            harness.extension._runner = runner_mock
            harness.trigger_event(SUT_RESET_STARTED, MOCK_ENDPOINT, entity=entity, data=False)
            harness.trigger_event(SUT_RESET_STARTED, MOCK_ENDPOINT, entity=entity, data=False)
            harness.trigger_event(SUT_RESET_DONE, MOCK_ENDPOINT, entity=entity, data=False)
            runner_mock.resume_execution.wait_for_call(timeout=TIMEOUT)
            self.assertEqual(runner_mock.pause_execution.call_count, 2)

    def test_not_resuming_if_other_sut_is_being_reset(self):
        """Execution is not resumed if another SUT is being reset."""
        with self.create_harness() as harness:
            runner_mock = SyncMock()
            runner_mock.pause_execution = SyncMock()
            runner_mock.resume_execution = SyncMock()
            entity1 = MagicMock()
            entity2 = MagicMock()
            harness.extension._runner = runner_mock
            harness.trigger_event(SUT_RESET_STARTED, MOCK_ENDPOINT, entity=entity1, data=False)
            harness.trigger_event(SUT_RESET_STARTED, MOCK_ENDPOINT, entity=entity2, data=False)
            harness.trigger_event(SUT_RESET_DONE, MOCK_ENDPOINT, entity=entity1, data=False)
            runner_mock.pause_execution.wait_for_call(timeout=TIMEOUT)
            runner_mock.pause_execution.wait_for_call(timeout=TIMEOUT)
            self.assertEqual(runner_mock.resume_execution.call_count, 0)
            harness.trigger_event(SUT_RESET_DONE, MOCK_ENDPOINT, entity=entity2, data=False)
            runner_mock.resume_execution.wait_for_call(timeout=TIMEOUT)

    def test_reset_done_without_reset_started_is_allowed(self):
        """Receiving SUT_RESET_DONE without prior SUT_RESET_STARTED is okay."""
        with self.create_harness() as harness:
            runner_mock = SyncMock()
            runner_mock.resume_execution = SyncMock()
            entity = MagicMock()
            harness.extension._runner = runner_mock
            harness.trigger_event(SUT_RESET_DONE, MOCK_ENDPOINT, entity=entity, data=False)
            runner_mock.resume_execution.wait_for_call(timeout=TIMEOUT)
