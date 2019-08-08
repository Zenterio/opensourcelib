"""The test runners internal representation of test cases."""

import enum
import inspect
import logging
import threading
import uuid
from textwrap import dedent

from zaf.extensions.extension import get_logger_name

from k2.runner import EXTENSION_NAME
from k2.runner.exceptions import DisabledException, SkipException
from k2.runner.timeout import get_timeout
from k2.utils.string import make_valid_filename

logger = logging.getLogger(get_logger_name('k2', EXTENSION_NAME, 'testcase'))
logger.addHandler(logging.NullHandler())


@enum.unique
class Verdict(enum.IntEnum):
    # Starting at zero to be able to map to exit code
    PASSED = 0
    FAILED = 1  # An AssertionError exception was raised
    ERROR = 2  # Any non-AssertionError exception was raised
    PENDING = 3  # Test case has not yet run
    SKIPPED = 4  # Not run due to missing but not failing precondition
    IGNORED = 5  # Not run due to configuration

    def combine(self, other):
        if self == Verdict.ERROR or other == Verdict.ERROR:
            return Verdict.ERROR
        if self == Verdict.PENDING or other == Verdict.PENDING:
            return Verdict.ERROR
        if self == Verdict.FAILED or other == Verdict.FAILED:
            return Verdict.FAILED
        return Verdict.PASSED


class TestCaseExecutionContext(object):
    """The test runners internal representation of the context a test case is executed in."""

    def __init__(self):
        self.lock = threading.RLock()
        self.thread_id = None

    def __enter__(self):
        with self.lock:
            self.thread_id = threading.get_ident()

    def __exit__(self, *exc_info):
        with self.lock:
            self.thread_id = None


class RunnerTestCase(object):
    """
    The test runners internal representation of a test case.

    Describes what context a test case should run in and how to run it.
    Provides information about the test cases execution status.
    """

    __test__ = False

    def __init__(self, run_function, name=None, params=None, filename_with_params=None):
        self.run = run_function
        self._name = run_function.__name__ if name is None else name
        self._filename_with_params = make_valid_filename(
            self._name) if filename_with_params is None else filename_with_params
        self._disabled = getattr(run_function, '_k2_disabled', False)
        self._disabled_message = getattr(run_function, '_k2_disabled_message', '')
        self.verdict = Verdict.PENDING
        self._execution_id = uuid.uuid1()
        self._execution_context = TestCaseExecutionContext()
        self._exception = None
        self._stacktrace = None
        self._params = params if params else []

    def __repr__(self):
        return self.run.__qualname__

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self._name

    @property
    def filename_with_params(self):
        return self._filename_with_params

    @property
    def params(self):
        return self._params

    @property
    def execution_id(self):
        return self._execution_id

    @property
    def disabled(self):
        return self._disabled

    @property
    def disabled_message(self):
        return self._disabled_message

    @property
    def qualified_name(self):
        return self._name

    @property
    def full_name(self):
        param_str = ''
        if self._params:
            param_str = '[{params}]'.format(params=','.join([str(p) for p in self._params]))
        return self.qualified_name + param_str

    @property
    def execution_context(self):
        return self._execution_context

    @property
    def timeout(self):
        return get_timeout(self.run)

    @property
    def exception(self):
        return self._exception

    @property
    def stacktrace(self):
        return self._stacktrace

    def update_verdict(self, exception=None, stacktrace=None):
        if exception is None:
            self.verdict = Verdict.PASSED
        elif isinstance(exception, SkipException):
            self.verdict = Verdict.SKIPPED
            self._exception = exception
            self._stacktrace = stacktrace
        elif isinstance(exception, DisabledException):
            self.verdict = Verdict.IGNORED
            self._exception = exception
            self._stacktrace = stacktrace
        elif isinstance(exception, AssertionError):
            self.verdict = Verdict.FAILED
            self._exception = exception
            self._stacktrace = stacktrace
        else:
            self.verdict = Verdict.ERROR
            self._exception = exception
            self._stacktrace = stacktrace

        logger.debug(
            'Test case {name} verdict changed to {result}'.format(
                name=self, result=self.verdict.name))

        if self._stacktrace:
            logger.debug('Test case stacktrace:\n{stacktrace}'.format(stacktrace=self._stacktrace))

    @property
    def description(self):
        return dedent(self.run.__doc__).strip() if self.run.__doc__ else ''

    def test_case_class(self):
        if inspect.ismethod(self.run):
            return self.run.__self__.__class__
        else:
            return None

    def test_case_module(self):
        return inspect.getmodule(self.run)

    @classmethod
    def from_test_case_definition(cls, test_case_definition):
        return RunnerTestCase(
            test_case_definition.run_function, test_case_definition.name,
            test_case_definition.params, test_case_definition.filename_with_params)
