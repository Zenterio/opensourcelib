"""Collects test results and sends out the collection in :ref:`message-TEST_RESULTS_COLLECTED`."""

import logging
from collections import OrderedDict, namedtuple

from zaf.component.decorator import requires
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import GET_RUN_VERDICT, RUN_COMMAND, RUN_COMMAND_ENDPOINT
from k2.results import RESULTS_ENDPOINT, TEST_RESULTS_COLLECTED
from k2.runner.messages import TEST_CASE_FINISHED, TEST_CASE_SKIPPED, TEST_CASE_STARTED, \
    TEST_RUN_FINISHED, TEST_RUN_STARTED, TestCaseFinished, TestCaseSkipped, TestCaseStarted, \
    TestRunFinished, TestRunStarted
from k2.runner.testcase import Verdict

logger = logging.getLogger(get_logger_name('k2', 'testresults'))
logger.addHandler(logging.NullHandler())

ResultsCollection = namedtuple('ResultsCollection', ['test_results', 'run_result'])


@CommandExtension(
    name='testresults',
    extends=[RUN_COMMAND],
    endpoints_and_messages={RESULTS_ENDPOINT: [TEST_RESULTS_COLLECTED]},
    groups=['test-results'],
)
class TestResults(AbstractExtension):
    """Collects test results."""

    def __init__(self, config, instances):
        self._test_results = OrderedDict()
        self._run_result = None

    @callback_dispatcher(
        [
            TEST_CASE_STARTED, TEST_CASE_FINISHED, TEST_CASE_SKIPPED, TEST_RUN_STARTED,
            TEST_RUN_FINISHED
        ])
    @requires(messagebus='MessageBus')
    def receive_test_message(self, message, messagebus):
        data = message.data
        if isinstance(data, TestCaseStarted):
            self._test_results[data.execution_id] = TestCaseResult(
                data.name, data.qualified_name, data.time, data.params, data.owner)
        elif isinstance(data, TestCaseFinished):
            self._test_results[data.execution_id].set_finished(
                data.time, data.verdict, data.exception, data.stacktrace, data.owner)
        elif isinstance(data, TestRunStarted):
            self._run_result = TestRunResult(data.name, data.time, data.owner)
        elif isinstance(data, TestRunFinished):
            self._run_result.set_finished(data.time, data.verdict, data.message, data.owner)
            messagebus.trigger_event(
                TEST_RESULTS_COLLECTED,
                RESULTS_ENDPOINT,
                data=ResultsCollection(list(self._test_results.values()), self._run_result))
        elif isinstance(data, TestCaseSkipped):
            self._test_results[data.execution_id] = TestCaseResult(
                data.name, data.qualified_name, data.time, data.owner)
            self._test_results[data.execution_id].set_finished(
                data.time, Verdict.SKIPPED, exception=None, stacktrace=None, owner=data.owner)

    @callback_dispatcher([GET_RUN_VERDICT], [RUN_COMMAND_ENDPOINT])
    def receive_run_command_message(self, message):
        return self._run_result.verdict


class TestRunResult(object):

    def __init__(self, name, time, owner=None):
        self._name = name
        self._start_time = time
        self._end_time = None
        self._message = None
        self._verdict = Verdict.PENDING
        self._owner = owner

    def set_finished(self, time, verdict, message='', owner=None):
        self._end_time = time
        self._verdict = verdict
        self._message = message
        if owner is not None:
            self._owner = owner
        return self

    @property
    def name(self):
        return self._name

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def duration(self):
        try:
            return self._end_time - self._start_time
        except TypeError:
            return None

    @property
    def verdict(self):
        return self._verdict

    @property
    def message(self):
        return self._message

    @property
    def owner(self):
        return self._owner


class TestCaseResult(object):

    def __init__(self, name, qualified_name, time, params=None, owner=None):
        self._name = name
        self._qualified_name = qualified_name
        self._start_time = time
        self._end_time = None
        self._verdict = Verdict.PENDING
        self._exception = None
        self._stacktrace = None
        self._params = params
        self._owner = owner

    def set_finished(self, time, verdict, exception, stacktrace, owner=None):
        self._end_time = time
        self._verdict = verdict
        self._exception = exception
        self._stacktrace = stacktrace
        if owner is not None:
            self._owner = owner
        return self

    @property
    def name(self):
        return self._name

    @property
    def qualified_name(self):
        return self._qualified_name

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def duration(self):
        try:
            return self._end_time - self._start_time
        except TypeError:
            return None

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
    def params(self):
        return self._params or []

    @property
    def owner(self):
        return self._owner
