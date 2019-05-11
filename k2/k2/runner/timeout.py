"""
Keeps track of how long a test case has been running.

Should a test case exceed its maximum execution time, a ABORT_TEST_CASE_REQUEST
is set to the test runner.

"""

import logging
import threading

from zaf.component.decorator import requires
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.runner import ABORT_TEST_CASE_REQUEST, EXTENSION_NAME, RUNNER_ENDPOINT, \
    TEST_CASE_FINISHED, TEST_CASE_STARTED
from k2.runner.messages import AbortTestCaseRequest, TestCaseFinished, TestCaseStarted

logger = logging.getLogger(get_logger_name('k2', EXTENSION_NAME, 'timeout'))
logger.addHandler(logging.NullHandler())


def timeout(seconds):
    """
    Decorate a test case with @timeout to annotate the maximum execution time.

    Example usage:

    .. code-block:: python

        # This test will fail if it takes longer than half a second to run.
        @timeout(seconds=0.5)
        def test_my_feature():
            pass
    """

    if callable(seconds):
        raise TypeError('The @timeout decorator may not be used without arguments.')

    if seconds < 0:
        raise ValueError('The @timeout decorator only accepts positive values.')

    def add_timeout(fn):
        if hasattr(fn, '_k2_test_case_timeout'):
            raise TypeError('The @timeout decorator may not be applied multiple times.')
        fn._k2_test_case_timeout = seconds
        return fn

    return add_timeout


def get_timeout(thing):
    try:
        if not hasattr(thing, '_k2_test_case_timeout'):
            thing = thing.__self__
    except AttributeError:
        pass
    if hasattr(thing, '_k2_test_case_timeout'):
        return thing._k2_test_case_timeout
    return None


class TimeoutError(Exception):
    pass


@CommandExtension(name='testcasetimeout', extends=[RUN_COMMAND])
class TestCaseTimeout(AbstractExtension):
    """Provides timeout functionality."""

    def __init__(self, config, instances):
        self._timers = {}

    @callback_dispatcher([TEST_CASE_STARTED, TEST_CASE_FINISHED])
    @requires(messagebus='MessageBus')
    def receive_test_message(self, message, messagebus):
        if isinstance(message.data, TestCaseStarted) and message.data.timeout is not None:
            self._start_timeout_timer(message.data, messagebus)
        if isinstance(message.data, TestCaseFinished):
            self._stop_timeout_timer(message.data)

    def _start_timeout_timer(self, message, messagebus):

        def send_abort_test_case():
            logger.info(
                'Test case {name} took longer than {timeout} seconds to run'.format(
                    name=message.name, timeout=message.timeout))
            request = AbortTestCaseRequest(message.execution_id, TimeoutError)
            messagebus.send_request(
                ABORT_TEST_CASE_REQUEST, RUNNER_ENDPOINT, data=request).wait(timeout=5)

        logger.debug(
            'Registering a timeout of {timeout} seconds for test case {name}'.format(
                timeout=message.timeout, name=message.name))
        timer = threading.Timer(message.timeout, send_abort_test_case)
        timer.start()
        self._timers[message.execution_id] = timer

    def _stop_timeout_timer(self, message):
        if message.execution_id in self._timers:
            logger.debug(
                'Deregistering timeout handler for test case {name}'.format(name=message.name))
            self._timers[message.execution_id].cancel()
            del self._timers[message.execution_id]
