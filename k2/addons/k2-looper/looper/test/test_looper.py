from unittest import TestCase

from zaf.config import MutuallyExclusiveConfigOptions
from zaf.messages.dispatchers import LocalMessageQueue

from k2.runner import TEST_RUN_STARTED
from k2.scheduler import ADD_TEST_CASES, RUN_QUEUE_EMPTY, RUN_QUEUE_INITIALIZED, SCHEDULER_ENDPOINT
from looper.test.utils import create_harness


class TestLooper(TestCase):

    def test_looper_does_not_register_dispatchers_if_not_configured(self):
        with create_harness() as harness:
            assert harness.extension._run_queue_empty_dispatcher is None
            assert harness.extension._test_run_started_dispatcher is None
            assert harness.extension._run_queue_initialized_dispatcher is None

    def test_looper_registers_init_dispatcher_if_repeat_configured(self):
        with create_harness(repeats=2) as harness:
            assert harness.extension._run_queue_empty_dispatcher is None
            assert harness.extension._test_run_started_dispatcher is None
            assert harness.extension._run_queue_initialized_dispatcher

    def test_looper_registers_both_dispatchers_if_duration_configured(self):
        with create_harness(duration='2') as harness:
            assert harness.extension._run_queue_empty_dispatcher
            assert harness.extension._run_queue_initialized_dispatcher
            assert harness.extension._test_run_started_dispatcher

    def test_looper_throws_exception_if_both_configured(self):
        with self.assertRaises(MutuallyExclusiveConfigOptions):
            with create_harness(duration='2', repeats=2):
                pass

    def test_looper_refills_test_queue_if_empty_with_duration_remaining(self):
        with create_harness(duration='2') as harness:
            harness.trigger_event(TEST_RUN_STARTED, SCHEDULER_ENDPOINT)
            harness.trigger_event(
                RUN_QUEUE_INITIALIZED, SCHEDULER_ENDPOINT, data=['test1', 'test2', 'test3'])
            with LocalMessageQueue(harness.messagebus, [ADD_TEST_CASES],
                                   [SCHEDULER_ENDPOINT]) as queue:
                harness.trigger_event(RUN_QUEUE_EMPTY, SCHEDULER_ENDPOINT)
                result = queue.get(timeout=1)
                assert result.data == ['test1']

    def test_looper_extends_test_queue_when_repeat_set(self):
        with create_harness(repeats=3) as harness:
            with LocalMessageQueue(harness.messagebus, [ADD_TEST_CASES],
                                   [SCHEDULER_ENDPOINT]) as queue:
                harness.trigger_event(
                    RUN_QUEUE_INITIALIZED, SCHEDULER_ENDPOINT, data=['test1', 'test2', 'test3'])
                result = queue.get(timeout=1)
                assert result.data == ['test1', 'test2', 'test3'] * 2
