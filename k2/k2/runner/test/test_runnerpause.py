import logging
import unittest
from contextlib import contextmanager
from queue import Queue
from threading import Event, Thread
from unittest.mock import Mock

from zaf.component.factory import Factory
from zaf.component.manager import ComponentManager
from zaf.extensions.extension import get_logger_name

from k2.finder.testfinder import TestCaseDefinition
from k2.runner import TEST_CASE_FINISHED, TEST_CASE_STARTED, TEST_RUN_FINISHED, TEST_RUN_STARTED
from k2.scheduler import SCHEDULE_NEXT_TEST

from ..exceptions import ExecutionPausedTooLong
from ..runner import TestRunner
from ..testcase import Verdict

logger = logging.getLogger(get_logger_name('k2', 'test'))
logger.addHandler(logging.NullHandler())


class TestTestRunnerHaltExecution(unittest.TestCase):

    TIMEOUT = 1

    def setUp(self):
        logger.debug('setUp')
        self.exception = None
        self.t = None
        self.tr = None
        self.run_queue = []
        self.message_queue = Queue()
        messagebus = Mock()

        self.unblock_testcase = Event()
        self.reached_testcase = Event()

        def send_request(message_id, endpoint_id=None, entities=None, data=None):
            logger.debug('send request id={id}'.format(id=str(message_id)))
            futures = Mock()
            if message_id == SCHEDULE_NEXT_TEST:
                future = Mock()
                if self.run_queue:
                    future.result.return_value = self.run_queue.pop(0)
                else:
                    future.result.return_value = None

                futures.wait.return_value = [future]
            return futures

        def trigger_event(message_id, endpoint_id=None, entities=None, data=None):
            logger.debug('trigger event id={id}'.format(id=str(message_id)))
            self.message_queue.put((message_id, endpoint_id, entities, data))

        messagebus.send_request.side_effect = send_request
        messagebus.trigger_event.side_effect = trigger_event

        self.tr = TestRunner(
            messagebus=messagebus,
            component_factory=Factory(ComponentManager()),
            suite_name='suite')
        self.tr.QUEUE_TIMEOUT_SECONDS = self.TIMEOUT / 2
        self.tr.EXECUTION_PAUSED_TIMEOUT_SECONDS = self.TIMEOUT

    def tearDown(self):
        logger.debug('tearDown')
        self.run_finish()

    def add_testcase(self):

        def my_test_case():
            logger.debug('Entering test case')
            self.reached_testcase.set()
            self.unblock_testcase.wait(timeout=self.TIMEOUT)
            logger.debug('Leaving test case')

        self.run_queue.append(TestCaseDefinition(my_test_case))

    def run_start(self):

        def wrapper():
            try:
                self.tr.run()
            except Exception as e:
                self.exception = e

        self.t = Thread(target=wrapper)
        self.t.start()
        id, _, _, _ = self.message_queue.get(timeout=self.TIMEOUT)
        self.assertEqual(id, TEST_RUN_STARTED)

    def run_finish(self):
        logger.debug('run_finish')
        if self.t:
            try:
                self.t.join()
                id = None
                if not self.message_queue.empty():
                    id, _, _, _ = self.message_queue.get(timeout=self.TIMEOUT)  # test run finished
                if self.exception:
                    logger.debug('run finish thread exception e={e}'.format(e=str(self.exception)))
                    raise self.exception
                if id:
                    self.assertEqual(id, TEST_RUN_FINISHED)
                logger.debug('run_finish completed')
            finally:
                self.t = None
                self.exception = None

    @contextmanager
    def during_testcase(self):
        try:
            logger.debug('during_testcase')
            id, _, _, _ = self.message_queue.get(timeout=self.TIMEOUT)  # test case started event
            self.assertEqual(id, TEST_CASE_STARTED)
            self.reached_testcase.wait(timeout=self.TIMEOUT)  # reached test case
            logger.debug('during_testcase starting context')
            yield
            logger.debug('no exception during test case')
        finally:
            logger.debug('during_testcase cleanup')
            self.unblock_testcase.set()
            id, _, _, _ = self.message_queue.get(timeout=self.TIMEOUT)  # test case finished
            self.assertEqual(id, TEST_CASE_FINISHED)
            self.unblock_testcase.clear()
            self.reached_testcase.clear()
            logger.debug('during_testcase cleanup completed')

    def test_pause_and_resume_and_associated_states(self):
        """
        Test pause execution and resume execution and associated states.

        * is_running is true when execution started, and when pause has been requested
          but a test case is still running.
        * is_paused is true when execution has been started, but is paused and no
          test case is actively running.
        * is_stopped is true when execution has not started and when it has finished
        """
        self.add_testcase()
        self.add_testcase()

        # before run
        self.assertFalse(self.tr.is_running)
        self.assertFalse(self.tr.is_paused)
        self.assertTrue(self.tr.is_stopped)

        try:
            self.run_start()

            with self.during_testcase():
                # In test case, we are running
                self.assertTrue(self.tr.is_running)
                self.assertFalse(self.tr.is_paused)
                self.assertFalse(self.tr.is_stopped)

                self.tr.pause_execution()

                # Pausing the execution is not enough, test case still running
                self.assertTrue(self.tr.is_running)
                self.assertFalse(self.tr.is_paused)
                self.assertFalse(self.tr.is_stopped)

            # We have to wait for current test case to finish before is_paused.
            self.assertTrue(self.tr.is_paused)
            self.assertFalse(self.tr.is_running)
            self.assertFalse(self.tr.is_stopped)
            self.assertEqual(len(self.tr.run_history), 1)
        finally:
            self.tr.resume_execution()
            # second test case
            with self.during_testcase():
                pass

        self.run_finish()
        self.assertFalse(self.tr.is_paused)
        self.assertFalse(self.tr.is_running)
        self.assertTrue(self.tr.is_stopped)
        self.assertEqual(len(self.run_queue), 0)
        self.assertEqual(len(self.tr.run_history), 2)

    def test_pause_and_resume_execution_can_be_called_multiple_times_in_a_row(self):
        """
        Pause and resume execution can be called multiple times in row without locking.

        Additional calls to pause_execution has no effect if already paused.
        A single call to resume execution is enough for resuming, despite
        multiple pause.
        """
        self.add_testcase()
        self.add_testcase()

        try:
            self.run_start()

            with self.during_testcase():
                # Multiple pause in a row is allowed
                self.tr.pause_execution()
                self.tr.pause_execution()

            self.assertTrue(self.tr.is_paused)
        finally:
            self.tr.resume_execution()
            # First resume is enough to start execution again
            self.assertFalse(self.tr.is_paused)
            # Multiple resume is allowed
            self.tr.resume_execution()
            # second test case
            with self.during_testcase():
                pass
        self.run_finish()
        self.assertTrue(self.tr.is_stopped)

    def test_pause_and_resume_execution_can_be_called_multiple_cicles(self):
        """
        Supports multiple cicles of pause and resume execution.

        Pause and resume can be done again after first cicle of pause-resume.
        """
        self.add_testcase()
        self.add_testcase()
        self.add_testcase()

        try:
            self.run_start()

            with self.during_testcase():
                self.tr.pause_execution()
            self.assertTrue(self.tr.is_paused)

            self.tr.resume_execution()

            with self.during_testcase():
                self.tr.pause_execution()
            self.assertTrue(self.tr.is_paused)
        finally:
            self.tr.resume_execution()
            self.assertFalse(self.tr.is_paused)
            # third test case
            with self.during_testcase():
                pass
        self.run_finish()
        self.assertTrue(self.tr.is_stopped)

    def test_raises_exception_if_wait_for_resume_is_too_long(self):
        """
        Raises exception if wait for resume is too long.

        The runner raises an ExecutionPausedTooLong if the execution
        is paused and the command loop is stalled for more than,
        EXECUTION_PAUSED_TIMEOUT_SECONDS.
        """
        self.add_testcase()
        self.run_start()
        self.tr.EXECUTION_PAUSED_TIMEOUT_SECONDS = 0
        with self.during_testcase():
            self.tr.pause_execution()
        with self.assertRaises(ExecutionPausedTooLong):
            self.run_finish()

    def test_abort_during_testcase_is_delayed_until_execution_resumes(self):
        """
        Abort, during test case in progress, is delayed until execution resumes.

        If aborted (non-critical), while being paused, the execution is not
        automatically resumed. Instead the abort is delayed until the runner
        resumes.
        """
        self.add_testcase()
        self.add_testcase()

        self.run_start()

        with self.during_testcase():
            self.tr.pause_execution()
            self.tr.abort_run_after_current_test_cases_have_completed()
        # We are still paused even though abort requested.
        self.assertTrue(self.tr.is_paused)

        self.tr.resume_execution()
        self.message_queue.get(timeout=self.TIMEOUT)  # skipped test case
        self.run_finish()

        self.assertEqual(len(self.run_queue), 0)
        self.assertEqual(len(self.tr.run_history), 2)
        self.assertEqual(self.tr.run_history[0].verdict, Verdict.PASSED)
        self.assertEqual(self.tr.run_history[1].verdict, Verdict.SKIPPED)

    def test_abort_inbetween_testcase_is_delayed_until_execution_resumes(self):
        """
        Abort, inbetween test case in progress, is delayed until execution resumes.

        If aborted (non-critical), while being paused, the execution is not
        automatically resumed. Instead the abort is delayed until the runner
        resumes.
        """
        self.add_testcase()
        self.add_testcase()

        self.run_start()

        with self.during_testcase():
            self.tr.pause_execution()

        self.tr.abort_run_after_current_test_cases_have_completed()
        # We are still paused even though abort requested.
        self.assertTrue(self.tr.is_paused)

        self.tr.resume_execution()
        self.message_queue.get(timeout=self.TIMEOUT)  # skipped test case
        self.run_finish()

        self.assertEqual(len(self.run_queue), 0)
        self.assertEqual(len(self.tr.run_history), 2)
        self.assertEqual(self.tr.run_history[0].verdict, Verdict.PASSED)
        self.assertEqual(self.tr.run_history[1].verdict, Verdict.SKIPPED)

    def test_immediate_abort_during_testcase_resumes_execution(self):
        """
        Immediate abort aborts right away by resuming execution.

        If immediate aborted (critical), test case in progress, while being paused,
        the execution is automatically resumed. The abort is handled directly
        and the runner is stopped immediately.
        """
        self.add_testcase()
        self.add_testcase()

        self.run_start()

        with self.during_testcase():
            self.tr.pause_execution()
            self.tr.abort_run_immediately()
        # We are not paused any more after immediate abort.
        self.assertFalse(self.tr.is_paused)

        self.message_queue.get(timeout=self.TIMEOUT)  # skipped test case
        self.run_finish()

        self.assertEqual(len(self.run_queue), 0)
        self.assertEqual(len(self.tr.run_history), 2)
        # Race condition if abort will actually have time to raise the abort
        # exception, and we therefore don't know the verdict of the first
        # test case, it can be either pass or error. Hence no check for first
        # test case.
        self.assertEqual(self.tr.run_history[1].verdict, Verdict.SKIPPED)

    def test_immediate_abort_inbetween_testcase_resumes_execution(self):
        """
        Immediate abort aborts right away by resuming execution.

        If immediate aborted (critical), inbetween test cases, while being paused,
        the execution is automatically resumed. The abort is handled directly
        and the runner is stopped immediately.
        """
        self.add_testcase()
        self.add_testcase()

        self.run_start()

        with self.during_testcase():
            self.tr.pause_execution()
        self.assertTrue(self.tr.is_paused)

        # We are not paused any more after immediate abort.
        self.tr.abort_run_immediately()
        self.assertFalse(self.tr.is_paused)

        self.message_queue.get(timeout=self.TIMEOUT)  # skipped test case
        self.run_finish()

        self.assertEqual(len(self.run_queue), 0)
        self.assertEqual(len(self.tr.run_history), 2)
        self.assertEqual(self.tr.run_history[1].verdict, Verdict.SKIPPED)
