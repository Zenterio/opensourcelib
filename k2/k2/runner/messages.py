import datetime

from zaf.builtin.logging import ENTER_LOG_SCOPE, EXIT_LOG_SCOPE, LOG_END_POINT, LogScopeMessageData

from k2 import ABORT
from k2.runner import ABORT_TEST_CASE_REQUEST, RUNNER_ENDPOINT, TEST_CASE_FINISHED, \
    TEST_CASE_SKIPPED, TEST_CASE_STARTED, TEST_RUN_FINISHED, TEST_RUN_STARTED


class TestCaseStarted(object):

    def __init__(
            self, execution_id, name, qualified_name, time, timeout=None, owner=None, params=None):
        self._execution_id = execution_id
        self._name = name
        self._qualified_name = qualified_name
        self._time = time
        self._timeout = timeout
        self._owner = owner
        self._params = params

    @property
    def execution_id(self):
        return self._execution_id

    @property
    def name(self):
        return self._name

    @property
    def qualified_name(self):
        return self._qualified_name

    @property
    def time(self):
        return self._time

    @property
    def timeout(self):
        return self._timeout

    @property
    def owner(self):
        return self._owner

    @property
    def params(self):
        return self._params

    def __str__(self):
        return 'Test case {name} started'.format(name=self.name)


class TestCaseFinished(object):

    def __init__(
            self, execution_id, name, time, verdict, exception=None, stacktrace=None, owner=None):
        self._execution_id = execution_id
        self._name = name
        self._time = time
        self._verdict = verdict
        self._exception = exception
        self._stacktrace = stacktrace
        self._owner = owner

    @property
    def execution_id(self):
        return self._execution_id

    @property
    def name(self):
        return self._name

    @property
    def time(self):
        return self._time

    @property
    def verdict(self):
        return self._verdict

    @property
    def exception(self):
        return self._exception

    @property
    def stacktrace(self):
        return self._stacktrace

    @property
    def owner(self):
        return self._owner

    def __str__(self):
        return 'Test case {name} finished with verdict {verdict}'.format(
            name=self.name, verdict=self.verdict.name)


class TestCaseSkipped(object):

    def __init__(self, execution_id, name, qualified_name, time, reason, owner=None):
        self._execution_id = execution_id
        self._name = name
        self._qualified_name = qualified_name
        self._time = time
        self._reason = reason
        self._owner = owner

    @property
    def execution_id(self):
        return self._execution_id

    @property
    def name(self):
        return self._name

    @property
    def qualified_name(self):
        return self._qualified_name

    @property
    def time(self):
        return self._time

    @property
    def reason(self):
        return self._reason

    @property
    def owner(self):
        return self._owner


class TestRunStarted(object):

    def __init__(self, name, time, owner=None):
        self._name = name
        self._time = time
        self._owner = owner

    def __str__(self):
        return 'Test Run Started'

    @property
    def name(self):
        return self._name

    @property
    def time(self):
        return self._time

    @property
    def owner(self):
        return self._owner


class TestRunFinished(object):

    def __init__(self, time, verdict, message, owner=None):
        self._time = time
        self._verdict = verdict
        self._message = message
        self._owner = owner

    def __str__(self):
        return 'Test Run Finished'

    @property
    def time(self):
        return self._time

    @property
    def verdict(self):
        return self._verdict

    @property
    def message(self):
        return self._message

    @property
    def owner(self):
        return self._owner


class AbortTestCaseRequest(object):

    def __init__(self, execution_id, exception_type):
        """
        Instruct the test runner to abort a test case.

        :param execution_id: Execution id of the test case to interrupt.
        :param exception_type: Type of the exception to raise in the thread
                               running the test case to abort it.
        """
        self._execution_id = execution_id
        self._exception_type = exception_type

    @property
    def execution_id(self):
        return self._execution_id

    @property
    def exception_type(self):
        return self._exception_type


def runner_endpoint_with_messages():
    """
    Define TestRunner endpoint and messages in an messagebus.

    :return: dict from EndpointId to list of MessageIds
    """
    return {
        RUNNER_ENDPOINT: [
            TEST_RUN_STARTED, TEST_RUN_FINISHED, TEST_CASE_STARTED, TEST_CASE_FINISHED,
            TEST_CASE_SKIPPED, ABORT_TEST_CASE_REQUEST, ABORT
        ],
    }


def trigger_test_run_started(messagebus, name):
    messagebus.trigger_event(
        TEST_RUN_STARTED, RUNNER_ENDPOINT, data=TestRunStarted(name, datetime.datetime.now()))


def trigger_test_run_finished(messagebus, verdict, message):
    messagebus.trigger_event(
        TEST_RUN_FINISHED,
        RUNNER_ENDPOINT,
        data=TestRunFinished(datetime.datetime.now(), verdict, message))


def trigger_test_case_started(messagebus, test_case):
    test_case_name = test_case.filename_with_params
    messagebus.send_request(
        ENTER_LOG_SCOPE, LOG_END_POINT,
        data=LogScopeMessageData('testcase', name=test_case_name)).wait(timeout=10)
    messagebus.trigger_event(
        TEST_CASE_STARTED,
        RUNNER_ENDPOINT,
        data=TestCaseStarted(
            test_case.execution_id,
            test_case.name,
            test_case.qualified_name,
            datetime.datetime.now(),
            test_case.timeout,
            params=[str(param) for param in test_case.params]))


def trigger_test_case_finished(messagebus, test_case):
    messagebus.trigger_event(
        TEST_CASE_FINISHED,
        RUNNER_ENDPOINT,
        data=TestCaseFinished(
            test_case.execution_id, test_case.name, datetime.datetime.now(), test_case.verdict,
            test_case.exception, test_case.stacktrace))
    test_case_name = test_case.filename_with_params
    messagebus.send_request(
        EXIT_LOG_SCOPE,
        LOG_END_POINT,
        data=LogScopeMessageData('testcase', name=test_case_name,
                                 result=test_case.verdict.name)).wait(timeout=10)


def trigger_test_case_skipped(messagebus, test_case, reason):
    messagebus.trigger_event(
        TEST_CASE_SKIPPED,
        RUNNER_ENDPOINT,
        data=TestCaseSkipped(
            test_case.execution_id, test_case.name, test_case.qualified_name,
            datetime.datetime.now(), reason))
