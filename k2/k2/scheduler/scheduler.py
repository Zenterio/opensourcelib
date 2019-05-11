"""
Handles the scheduling of test case.

Requests the initial set of test cases from the test finder, filters it using the config,
and then provides the test cases to the test runner.
The run queue can be modified during the run using requests.

If ABORT or CRITICAL_ABORT has been received no more test cases can be added to the run queue.
Remaining test cases will still be provided to the test runner so the correct verdict can be set on them.
"""
import re

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension
from zaf.messages.decorator import callback_dispatcher, concurrent_dispatcher

from k2 import ABORT, CRITICAL_ABORT
from k2.cmd.run import RUN_COMMAND
from k2.finder import FIND_TEST_CASES, FINDER_ENDPOINT
from k2.utils.threading import LockableList

from . import ADD_TEST_CASES, CLEAR_RUN_QUEUE, GET_CURRENT_RUN_QUEUE, GET_LAST_SCHEDULED_TEST, \
    REMOVE_TEST_CASES, RUN_QUEUE_EMPTY, RUN_QUEUE_INITIALIZED, RUN_QUEUE_MODIFIED, \
    SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT, SCHEDULING_NEXT_TEST, TESTS_EXCLUDE, \
    TESTS_EXCLUDE_REGEX, TESTS_INCLUDE, TESTS_INCLUDE_REGEX

EXTENSION_NAME = 'testscheduler'


@CommandExtension(
    name=EXTENSION_NAME,
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(TESTS_INCLUDE, required=False),
        ConfigOption(TESTS_INCLUDE_REGEX, required=False),
        ConfigOption(TESTS_EXCLUDE, required=False),
        ConfigOption(TESTS_EXCLUDE_REGEX, required=False),
    ],
    endpoints_and_messages={
        SCHEDULER_ENDPOINT: [
            SCHEDULE_NEXT_TEST, SCHEDULING_NEXT_TEST, ADD_TEST_CASES, REMOVE_TEST_CASES,
            RUN_QUEUE_EMPTY, CLEAR_RUN_QUEUE, GET_CURRENT_RUN_QUEUE, GET_LAST_SCHEDULED_TEST,
            RUN_QUEUE_INITIALIZED, RUN_QUEUE_MODIFIED
        ]
    })
class TestScheduler(AbstractExtension):

    def __init__(self, config, instances):
        self._include = config.get(TESTS_INCLUDE, [])
        self._include_re = config.get(TESTS_INCLUDE_REGEX, [])
        self._exclude = config.get(TESTS_EXCLUDE, [])
        self._exclude_re = config.get(TESTS_EXCLUDE_REGEX, [])

        self._run_queue = None
        self._last_scheduled = None
        self._aborted = False

    @concurrent_dispatcher(
        [
            SCHEDULE_NEXT_TEST, ADD_TEST_CASES, REMOVE_TEST_CASES, CLEAR_RUN_QUEUE,
            GET_CURRENT_RUN_QUEUE, GET_LAST_SCHEDULED_TEST
        ], [SCHEDULER_ENDPOINT])
    @requires(messagebus='MessageBus')
    def handle_api_messages(self, message, messagebus):
        if self._run_queue is None:
            self._initialize_test_cases(messagebus)
        if message.message_id == SCHEDULE_NEXT_TEST:
            return self._schedule_next_test_case(messagebus)
        elif message.message_id == GET_CURRENT_RUN_QUEUE:
            return self._get_current_run_queue()
        elif message.message_id == ADD_TEST_CASES:
            return self._add_test_cases(message.data, messagebus)
        elif message.message_id == REMOVE_TEST_CASES:
            return self._remove_test_cases(message.data, messagebus)
        elif message.message_id == CLEAR_RUN_QUEUE:
            return self._clear_run_queue()
        elif message.message_id == GET_LAST_SCHEDULED_TEST:
            return self._last_scheduled

    @callback_dispatcher([ABORT, CRITICAL_ABORT])
    def handle_abort(self, message):
        self._aborted = True

    def _initialize_test_cases(self, messagebus):
        run_queue = LockableList()
        if not self._aborted:
            for find_result in messagebus.send_request(FIND_TEST_CASES,
                                                       FINDER_ENDPOINT).wait(timeout=5):
                run_queue.extend(self._filter_using_config(find_result.result(timeout=5)))
        self._run_queue = run_queue

        messagebus.trigger_event(
            RUN_QUEUE_INITIALIZED, SCHEDULER_ENDPOINT, data=self._cloned_run_queue())

    def _filter_using_config(self, test_cases):
        split_includes = [include.split('.') for include in self._include]
        split_excludes = [exclude.split('.') for exclude in self._exclude]
        compiled_include_res = [re.compile(regex) for regex in self._include_re]
        compiled_exclude_res = [re.compile(regex) for regex in self._exclude_re]

        no_include_rules = len(split_includes) == 0 and len(compiled_include_res) == 0

        def include(test_case):
            if test_case.always_included:
                return True

            test_case_parts = test_case.name.split('.')
            to_be_included = no_include_rules

            if not to_be_included:
                for include_parts in split_includes:
                    if test_case_parts[:len(include_parts)] == include_parts:
                        to_be_included = True

            if not to_be_included:
                for include_re in compiled_include_res:
                    if include_re.search(test_case.name):
                        to_be_included = True

            if to_be_included:
                for exclude_parts in split_excludes:
                    if test_case_parts[:len(exclude_parts)] == exclude_parts:
                        to_be_included = False

            if to_be_included:
                for exclude_re in compiled_exclude_res:
                    if exclude_re.search(test_case.name):
                        to_be_included = False
            return to_be_included

        return list(filter(include, test_cases))

    def _schedule_next_test_case(self, messagebus):
        messagebus.trigger_event(SCHEDULING_NEXT_TEST, SCHEDULER_ENDPOINT)

        if len(self._run_queue) == 0:
            messagebus.trigger_event(RUN_QUEUE_EMPTY, SCHEDULER_ENDPOINT)

        if self._run_queue:
            with self._run_queue.lock:
                self._last_scheduled = self._run_queue.pop(0)
                return self._last_scheduled
        else:
            return None

    def _get_current_run_queue(self):
        with self._run_queue.lock:
            return self._cloned_run_queue()

    def _cloned_run_queue(self):
        return self._run_queue[::]

    def _add_test_cases(self, test_cases, messagebus):
        if not self._aborted:
            with self._run_queue.lock:
                self._run_queue.extend(test_cases)
                cloned_run_queue = self._cloned_run_queue()
            messagebus.trigger_event(RUN_QUEUE_MODIFIED, SCHEDULER_ENDPOINT, data=cloned_run_queue)

    def _remove_test_cases(self, test_cases, messagebus):
        with self._run_queue.lock:
            removed_tests = []
            for remove_test in test_cases:
                removed_tests.extend([test for test in self._run_queue.data if test == remove_test])
                self._run_queue.data = [
                    test for test in self._run_queue.data if test != remove_test
                ]
                cloned_run_queue = self._cloned_run_queue()
        messagebus.trigger_event(RUN_QUEUE_MODIFIED, SCHEDULER_ENDPOINT, data=cloned_run_queue)
        return removed_tests

    def _clear_run_queue(self):
        with self._run_queue.lock:
            removed_test_cases = self._run_queue.data[::]
            self._run_queue.clear()
            return removed_test_cases
