import unittest
from unittest.mock import Mock

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.messages.dispatchers import CallbackDispatcher

from k2 import ABORT, CRITICAL_ABORT, K2_APPLICATION_ENDPOINT
from k2.finder import FIND_TEST_CASES, FINDER_ENDPOINT
from k2.finder.testfinder import TestCaseDefinition, TestCaseFailureDefinition
from k2.runner import RUNNER_ENDPOINT

from .. import ADD_TEST_CASES, CLEAR_RUN_QUEUE, GET_CURRENT_RUN_QUEUE, GET_LAST_SCHEDULED_TEST, \
    REMOVE_TEST_CASES, RUN_QUEUE_EMPTY, RUN_QUEUE_INITIALIZED, RUN_QUEUE_MODIFIED, \
    SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT, SCHEDULING_NEXT_TEST, TESTS_EXCLUDE, \
    TESTS_EXCLUDE_REGEX, TESTS_INCLUDE, TESTS_INCLUDE_REGEX
from ..scheduler import TestScheduler


class TestScheduleNextTestCase(unittest.TestCase):

    def test_schedule_next_test_case_returns_first_test_case_from_finder(self):
        with create_harness([test1, test2]) as harness:
            actual = harness.send_request(SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual, test1)

    def test_schedule_next_test_case_returns_each_test_case_once(self):
        with create_harness([test1, test2]) as harness:
            actual1 = harness.send_request(SCHEDULE_NEXT_TEST,
                                           SCHEDULER_ENDPOINT).wait()[0].result()
            actual2 = harness.send_request(SCHEDULE_NEXT_TEST,
                                           SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual1, test1)
            self.assertEqual(actual2, test2)

    def test_schedule_next_test_case_returns_none_when_there_are_no_more_test_cases(self):
        with create_harness([test1, test2]) as harness:
            actual1 = harness.send_request(SCHEDULE_NEXT_TEST,
                                           SCHEDULER_ENDPOINT).wait()[0].result()
            actual2 = harness.send_request(SCHEDULE_NEXT_TEST,
                                           SCHEDULER_ENDPOINT).wait()[0].result()
            actual3 = harness.send_request(SCHEDULE_NEXT_TEST,
                                           SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual1, test1)
            self.assertEqual(actual2, test2)
            self.assertIsNone(actual3)


class TestAbort(unittest.TestCase):

    def test_abort_and_critical_abort_sets_aborted_to_true(self):
        with create_harness([test1, test2]) as harness:
            self.assertFalse(harness.extension._aborted)
            harness.trigger_event(ABORT, K2_APPLICATION_ENDPOINT)
            self.assertTrue(harness.extension._aborted)

        with create_harness([test1, test2]) as harness:
            self.assertFalse(harness.extension._aborted)
            harness.trigger_event(CRITICAL_ABORT, K2_APPLICATION_ENDPOINT)
            self.assertTrue(harness.extension._aborted)

    def test_add_tests_does_nothing_if_abort_has_been_received(self):
        with create_harness([test1, test2]) as harness:
            before = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                          SCHEDULER_ENDPOINT).wait()[0].result()
            harness.trigger_event(ABORT, K2_APPLICATION_ENDPOINT)
            harness.send_request(
                ADD_TEST_CASES, SCHEDULER_ENDPOINT, data=[test2]).wait()[0].result()
            self.assertEqual(harness.extension._run_queue, before)

    def test_initialize_test_cases_does_nothing_if_abort_has_been_received(self):
        with create_harness([test1, test2]) as harness:
            harness.trigger_event(ABORT, K2_APPLICATION_ENDPOINT)
            harness.extension._initialize_test_cases(Mock())
            self.assertEqual(harness.extension._run_queue, [])

    def test_existing_run_queue_remains_after_abort_is_received(self):
        with create_harness([test1, test2]) as harness:
            before = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                          SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(before, [test1, test2])
            harness.trigger_event(ABORT, K2_APPLICATION_ENDPOINT)
            after = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                         SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(before, after)


class TestAddTestCases(unittest.TestCase):

    def test_that_test_cases_can_be_added_before_first_next_test_case_is_requested(self):
        with create_harness([test1]) as harness:
            harness.send_request(ADD_TEST_CASES, SCHEDULER_ENDPOINT, data=[test2, test3]).wait()
            actual = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                          SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual, [test1, test2, test3])

    def test_that_test_cases_can_be_added_after_first_next_test_case_is_requested(self):
        with create_harness([test1]) as harness:
            harness.send_request(SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT).wait()[0].result()
            harness.send_request(
                ADD_TEST_CASES, SCHEDULER_ENDPOINT, data=[test2, test3]).wait()[0].result()
            actual = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                          SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual, [test2, test3])


class TestRemoveTestCases(unittest.TestCase):

    def test_that_test_cases_can_be_removed_after_first_next_test_case_is_requested(self):
        with create_harness([test1, test2, test3]) as harness:
            harness.send_request(SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT).wait()[0].result()
            harness.send_request(
                REMOVE_TEST_CASES, SCHEDULER_ENDPOINT, data=[test2]).wait()[0].result()
            actual = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                          SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual, [test3])

    def test_that_test_cases_can_be_removed_before_first_next_test_case_is_requested(self):
        with create_harness([test1, test2, test3]) as harness:
            harness.send_request(
                REMOVE_TEST_CASES, SCHEDULER_ENDPOINT, data=[test2]).wait()[0].result()
            actual = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                          SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual, [test1, test3])

    def test_that_duplicate_tests_are_all_removed(self):
        with create_harness([test2, test1, test2, test3, test2]) as harness:
            harness.send_request(
                REMOVE_TEST_CASES, SCHEDULER_ENDPOINT, data=[test2]).wait()[0].result()
            actual = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                          SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual, [test1, test3])

    def test_that_removed_tests_are_returned_to_requester(self):
        with create_harness([test2, test1, test2, test3, test2]) as harness:
            removed = harness.send_request(
                REMOVE_TEST_CASES, SCHEDULER_ENDPOINT, data=[test1, test3]).wait()[0].result()
            actual = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                          SCHEDULER_ENDPOINT).wait()[0].result()

            self.assertEqual(removed, [test1, test3])
            self.assertEqual(actual, [test2, test2, test2])

    def test_that_it_is_ok_to_call_remove_with_non_existing_tests(self):
        with create_harness([test2, test1, test2, test2]) as harness:
            removed = harness.send_request(
                REMOVE_TEST_CASES, SCHEDULER_ENDPOINT, data=[test3]).wait()[0].result()
            actual = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                          SCHEDULER_ENDPOINT).wait()[0].result()

            self.assertEqual(removed, [])
            self.assertEqual(actual, [test2, test1, test2, test2])


class TestClearRunQueue(unittest.TestCase):

    def test_clear_run_queue(self):
        with create_harness([test1, test2, test3]) as harness:
            removed = harness.send_request(CLEAR_RUN_QUEUE, SCHEDULER_ENDPOINT).wait()[0].result()
            actual = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                          SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(removed, [test1, test2, test3])
            self.assertEqual(actual, [])


class TestGetCurrentRunQueue(unittest.TestCase):

    def test_get_current_run_queue_returns_the_remaining_run_queue(self):
        with create_harness([test1, test2]) as harness:
            actual1 = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                           SCHEDULER_ENDPOINT).wait()[0].result()
            harness.send_request(SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT).wait()[0].result()
            actual2 = harness.send_request(GET_CURRENT_RUN_QUEUE,
                                           SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual1, [test1, test2])
            self.assertEqual(actual2, [test2])


class TestLastScheduledTest(unittest.TestCase):

    def test_that_last_scheduled_test_is_none_before_first_first_next_test_case_is_requested(self):
        with create_harness([test1, test2]) as harness:
            last_scheduled = harness.send_request(GET_LAST_SCHEDULED_TEST,
                                                  SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertIsNone(last_scheduled)

    def test_that_last_scheduled_test_changes_when_scheduling_next_test(self):
        with create_harness([test1, test2]) as harness:
            harness.send_request(SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT).wait()[0].result()
            last_scheduled1 = harness.send_request(GET_LAST_SCHEDULED_TEST,
                                                   SCHEDULER_ENDPOINT).wait()[0].result()
            harness.send_request(SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT).wait()[0].result()
            last_scheduled2 = harness.send_request(GET_LAST_SCHEDULED_TEST,
                                                   SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(last_scheduled1, test1)
            self.assertEqual(last_scheduled2, test2)


class TestEvents(unittest.TestCase):

    def test_that_run_queue_initialized_is_triggered(self):
        with create_harness([test1, test2]) as harness:
            global run_queue
            run_queue = None

            def handle_run_queue_initialized(message):
                global run_queue
                run_queue = message.data

            run_queue_empty_dispatcher = CallbackDispatcher(
                harness.messagebus, handle_run_queue_initialized)
            run_queue_empty_dispatcher.register([RUN_QUEUE_INITIALIZED], [SCHEDULER_ENDPOINT])

            harness.send_request(SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(run_queue, [test1, test2])

    def test_that_run_queue_is_empty_is_triggered(self):
        with create_harness([]) as harness:
            global run_queue_empty_called
            run_queue_empty_called = False

            def handle_run_queue_empty(message):
                global run_queue_empty_called
                run_queue_empty_called = True

            run_queue_empty_dispatcher = CallbackDispatcher(
                harness.messagebus, handle_run_queue_empty)
            run_queue_empty_dispatcher.register([RUN_QUEUE_EMPTY], [SCHEDULER_ENDPOINT])

            harness.send_request(SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT).wait()[0].result()
            assert run_queue_empty_called

    def test_that_its_possible_to_add_tests_when_dispatching_run_queue_is_empty_in_callback(self):
        with create_harness([]) as harness:

            def handle_run_queue_empty(message):
                harness.send_request(
                    ADD_TEST_CASES, SCHEDULER_ENDPOINT, data=[test1]).wait()[0].result()

            run_queue_empty_dispatcher = CallbackDispatcher(
                harness.messagebus, handle_run_queue_empty)
            run_queue_empty_dispatcher.register([RUN_QUEUE_EMPTY], [SCHEDULER_ENDPOINT])

            actual_test = harness.send_request(SCHEDULE_NEXT_TEST,
                                               SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual_test, test1)

    def test_that_run_queue_modified_is_triggered_from_add_test_cases(self):
        with create_harness([test1]) as harness:
            global run_queue
            run_queue = None

            def handle_run_queue_modified(message):
                global run_queue
                run_queue = message.data

            run_queue_empty_dispatcher = CallbackDispatcher(
                harness.messagebus, handle_run_queue_modified)
            run_queue_empty_dispatcher.register([RUN_QUEUE_MODIFIED], [SCHEDULER_ENDPOINT])

            harness.send_request(
                ADD_TEST_CASES, SCHEDULER_ENDPOINT, data=[test2]).wait()[0].result()
            self.assertEqual(run_queue, [test1, test2])

    def test_that_run_queue_modified_is_triggered_from_remove_test_cases(self):
        with create_harness([test1, test2]) as harness:
            global run_queue
            run_queue = None

            def handle_run_queue_modified(message):
                global run_queue
                run_queue = message.data

            run_queue_empty_dispatcher = CallbackDispatcher(
                harness.messagebus, handle_run_queue_modified)
            run_queue_empty_dispatcher.register([RUN_QUEUE_MODIFIED], [SCHEDULER_ENDPOINT])

            harness.send_request(
                REMOVE_TEST_CASES, SCHEDULER_ENDPOINT, data=[test1]).wait()[0].result()
            self.assertEqual(run_queue, [test2])


class TestSchedulingNextTest(unittest.TestCase):

    def test_that_scheduling_next_test_is_triggered(self):
        with create_harness([]) as harness:
            global scheduling_next_test_count
            scheduling_next_test_count = 0

            def handle_scheduling_next_test(message):
                global scheduling_next_test_count
                scheduling_next_test_count += 1

            run_queue_empty_dispatcher = CallbackDispatcher(
                harness.messagebus, handle_scheduling_next_test)
            run_queue_empty_dispatcher.register([SCHEDULING_NEXT_TEST], [SCHEDULER_ENDPOINT])

            harness.send_request(SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT).wait()[0].result()
            assert run_queue_empty_called

    def test_that_its_possible_to_add_tests_when_dispatching_scheduling_next_test_in_callback(self):
        with create_harness([]) as harness:

            def handle_scheduling_next_test(message):
                harness.send_request(
                    ADD_TEST_CASES, SCHEDULER_ENDPOINT, data=[test1]).wait()[0].result()

            run_queue_empty_dispatcher = CallbackDispatcher(
                harness.messagebus, handle_scheduling_next_test)
            run_queue_empty_dispatcher.register([SCHEDULING_NEXT_TEST], [SCHEDULER_ENDPOINT])

            actual_test = harness.send_request(SCHEDULE_NEXT_TEST,
                                               SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual_test, test1)

    def test_that_its_possible_to_remove_and_add_tests_when_dispatching_scheduling_next_test_in_callback(
            self):
        with create_harness([test1, test2]) as harness:

            def handle_scheduling_next_test(message):
                harness.send_request(
                    REMOVE_TEST_CASES, SCHEDULER_ENDPOINT, data=[test1, test2]).wait()[0].result()
                harness.send_request(
                    ADD_TEST_CASES, SCHEDULER_ENDPOINT, data=[test3]).wait()[0].result()

            run_queue_empty_dispatcher = CallbackDispatcher(
                harness.messagebus, handle_scheduling_next_test)
            run_queue_empty_dispatcher.register([SCHEDULING_NEXT_TEST], [SCHEDULER_ENDPOINT])

            actual_test = harness.send_request(SCHEDULE_NEXT_TEST,
                                               SCHEDULER_ENDPOINT).wait()[0].result()
            self.assertEqual(actual_test, test3)


class TestFilterUsingConfig(unittest.TestCase):

    def test_filter_without_config_returns_full_list(self):
        scheduler = TestScheduler({}, None)
        self.assertEqual(scheduler._filter_using_config(filter_tests), filter_tests)

    def test_matching_only_include_rule(self):
        scheduler = TestScheduler({TESTS_INCLUDE: ['pkg1']}, None)
        self.assertEqual(scheduler._filter_using_config(filter_tests), [filter_test1, filter_test2])

    def test_matching_only_include_re_rule(self):
        scheduler = TestScheduler({TESTS_INCLUDE_REGEX: [r'2\.mod']}, None)
        self.assertEqual(scheduler._filter_using_config(filter_tests), [filter_test1, filter_test2])

    def test_matching_only_exclude_rule(self):
        scheduler = TestScheduler({TESTS_EXCLUDE: ['pkg1']}, None)
        self.assertEqual(
            scheduler._filter_using_config(filter_tests),
            [filter_test3, filter_test4, filter_test5])

    def test_matching_only_exclude_re_rule(self):
        scheduler = TestScheduler({TESTS_EXCLUDE_REGEX: [r'2\.mod']}, None)
        self.assertEqual(
            scheduler._filter_using_config(filter_tests),
            [filter_test3, filter_test4, filter_test5])

    def test_matching_part_of_include_rule_is_filtered_out(self):
        scheduler = TestScheduler({TESTS_INCLUDE: ['pkg1.pkg']}, None)
        self.assertEqual(scheduler._filter_using_config(filter_tests), [])

    def test_matching_part_of_exclude_rule_is_not_filtered_out(self):
        scheduler = TestScheduler({TESTS_EXCLUDE: ['pkg1.pkg']}, None)
        self.assertEqual(scheduler._filter_using_config(filter_tests), filter_tests)

    def test_include_rule_matches_full_test_case_name(self):
        scheduler = TestScheduler({TESTS_INCLUDE: ['pkg3.mod1.test3']}, None)
        self.assertEqual(scheduler._filter_using_config(filter_tests), [filter_test3])

    def test_test_case_name_is_part_of_include(self):
        scheduler = TestScheduler({TESTS_INCLUDE: ['pkg3.mod1.test3.foo']}, None)
        self.assertEqual(scheduler._filter_using_config(filter_tests), [])

    def test_matching_one_of_include_or_include_re(self):

        def test_test_case_name_is_part_of_include(self):
            scheduler = TestScheduler(
                {
                    TESTS_INCLUDE: ['pkg1.pkg2'],
                    TESTS_INCLUDE_REGEX: [r'^.*test5']
                }, None)
            self.assertEqual(
                scheduler._filter_using_config(filter_tests),
                [filter_test1, filter_test2, filter_test5])

    def test_matching_one_of_exclude_or_exclude_re(self):

        def test_test_case_name_is_part_of_include(self):
            scheduler = TestScheduler(
                {
                    TESTS_EXCLUDE: ['pkg1.pkg2'],
                    TESTS_EXCLUDE_REGEX: [r'^.*test5']
                }, None)
            self.assertEqual(
                scheduler._filter_using_config(filter_tests), [filter_test3, filter_test4])

    def test_do_not_filter_out_always_include_tests(self):
        scheduler = TestScheduler({TESTS_INCLUDE: ['pkg1']}, None)
        self.assertEqual(scheduler._filter_using_config([always_include]), [always_include])


def create_harness(test_cases):
    harness = ExtensionTestHarness(
        TestScheduler,
        endpoints_and_messages={
            FINDER_ENDPOINT: [FIND_TEST_CASES],
            RUNNER_ENDPOINT: [ABORT],
            K2_APPLICATION_ENDPOINT: [ABORT, CRITICAL_ABORT],
        })

    def find_test_cases(message):
        return test_cases

    finder_dispatcher = CallbackDispatcher(harness.messagebus, find_test_cases)
    finder_dispatcher.register([FIND_TEST_CASES], [FINDER_ENDPOINT])

    return harness


test1 = TestCaseDefinition(Mock(), 'test1')
test2 = TestCaseDefinition(Mock(), 'test2')
test3 = TestCaseDefinition(Mock(), 'test3')

filter_test1 = TestCaseDefinition(Mock(), 'pkg1.pkg2.mod1.test1')
filter_test2 = TestCaseDefinition(Mock(), 'pkg1.pkg2.mod1.Class.test2')
filter_test3 = TestCaseDefinition(Mock(), 'pkg3.mod1.test3')
filter_test4 = TestCaseDefinition(Mock(), 'pkg3.mod2.test4')
filter_test5 = TestCaseDefinition(Mock(), 'pkg3.pkg4.mod3.test5')

filter_tests = [filter_test1, filter_test2, filter_test3, filter_test4, filter_test5]

always_include = TestCaseFailureDefinition(Mock(), 'not matching anything')
