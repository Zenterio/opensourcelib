import ctypes
import inspect
import logging
import threading
import traceback
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from zaf.component.factory import ExitScopeResult
from zaf.extensions.extension import get_logger_name

from k2.runner import EXTENSION_NAME, messages
from k2.runner.exceptions import DisabledException, ExecutionPausedTooLong, ScopeChangeException, \
    SkipException, TestCaseAborted
from k2.runner.testcase import RunnerTestCase, Verdict
from k2.scheduler import SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT
from k2.utils.interruptable import induce_spurious_wakeup_for_all_conditions_associated_with_thread
from k2.utils.threading import LockableList

logger = logging.getLogger(get_logger_name('k2', EXTENSION_NAME, 'runner'))
logger.addHandler(logging.NullHandler())


class Command(object):
    """Used internally by the test runner to define execution flow."""

    stop_running = 1
    next_test_case = 2
    run_test_case = 3

    _VALUES_TO_NAME = {
        1: 'stop_running',
        2: 'next_test_case',
        3: 'run_test_case',
    }

    def __init__(self, command_id, current_scope, test_case=None):
        self.command_id = command_id
        self.current_scope = current_scope
        self.test_case = test_case

    def __repr__(self):
        return '{command}: {testcase}'.format(
            command=Command._VALUES_TO_NAME[self.command_id],
            testcase=self.test_case.name if self.test_case else '')


RunResult = namedtuple('RunResult', ['scope', 'exception', 'stacktrace'])


class TestRunner(object):
    """The K2 test runner."""

    __test__ = False

    # A queue timeout of None makes the run loop wait for commands indefinately.
    QUEUE_TIMEOUT_SECONDS = None

    # How long the runner is allowed to wait for resuming execution in seconds.
    # If none, it will wait indefinately.
    EXECUTION_PAUSED_TIMEOUT_SECONDS = None

    def __init__(self, messagebus, component_factory, suite_name, parent_scope=None):
        self._suite_name = suite_name
        self._messagebus = messagebus
        self.run_history = LockableList()
        self.running_test_cases = LockableList()
        self.runner_scope = component_factory.enter_scope(
            scope='runner', parent=parent_scope, data=None)
        self._running = False
        self._abort = False
        self._command_queue = None
        self._execution_allowed = threading.Event()
        self._execution_allowed.set()
        self._abort_exceptions = []
        self.component_factory = component_factory
        self._command_response_map = {
            Command.stop_running: self._handle_stop_running_command,
            Command.next_test_case: self._handle_next_test_case_command,
            Command.run_test_case: self._handle_run_test_case_command,
        }

    def run(self, worker_count=1):
        """
        Run tests until the run queue is empty or stop() is called.

        This call is blocking and will block until the test run is either
        complete or stopped.
        """
        self._running = True
        self._abort = False
        self._command_queue = Queue()
        logger.info('Test run started')
        messages.trigger_test_run_started(self._messagebus, self._suite_name)

        for i in range(worker_count):
            self._post_command(Command(Command.next_test_case, self.runner_scope))

        with ThreadPoolExecutor(max_workers=worker_count) as self.executor:
            while self._running:
                command = self._command_queue.get(timeout=self.QUEUE_TIMEOUT_SECONDS)
                self._check_execution_allowed()
                logger.debug('Executing command: {command}'.format(command=str(command)))
                self._command_response_map[command.command_id](command)

        verdict = self._calculate_run_verdict()
        logger.info("Test run completed with verdict '{verdict}'".format(verdict=verdict.name))

        messages.trigger_test_run_finished(self._messagebus, verdict, self._run_failed_message())

    @property
    def is_running(self):
        """Return True if runner is running."""
        return self._running and not self.is_paused

    @property
    def is_paused(self):
        """Return True if runner is paused."""
        return self._running and \
            not self._execution_allowed.is_set() and \
            len(self.running_test_cases) == 0

    @property
    def is_stopped(self):
        """Return True if runner has been stopped."""
        return not self._running

    @property
    def is_aborted(self):
        """Return True if runner has been aborted."""
        return self._abort and self.is_stopped

    def abort_test_case(self, request):
        """Abort the currently running test by raising exception in execution thread."""
        with self.running_test_cases.lock:
            for test_case in self.running_test_cases:
                if test_case.execution_id == request.execution_id:
                    logger.info('Aborting test case {name}'.format(name=test_case))
                    _async_raise(test_case.execution_context.thread_id, request.exception_type)
                    return
        logger.warning(
            'Could not find a running test case with execution id {id}'.format(
                id=request.execution_id))

    def abort_run_after_current_test_cases_have_completed(self):
        """Abort the run after currently running test cases have completed."""
        logger.info('Aborting after running test cases have completed.')
        self._abort = True

    def abort_run_immediately(self):
        """Aborts the test run immediately by raising exception in execution thread."""
        logger.info('Aborting test run immediately!')
        self._abort = True
        with self.running_test_cases.lock:
            for test_case in self.running_test_cases:
                _async_raise(test_case.execution_context.thread_id, TestCaseAborted)
        self.resume_execution()

    def pause_execution(self):
        """Pause the execution."""
        if not self._abort:
            logger.info('Pausing execution of test run')
            self._execution_allowed.clear()

    def resume_execution(self):
        """Resume the execution (unpause)."""
        if not self._execution_allowed.is_set():
            logger.info('Resuming execution of test run')
            self._execution_allowed.set()

    def stop(self, current_scope):
        """
        Stop the runner.

        The runner will be stopped after the currently running test cases have
        completed.
        """
        logger.info('Stopping test run')
        self._post_command(Command(Command.stop_running, current_scope))

    def _check_execution_allowed(self):
        """Raise exception if waiting too long to allow execution, otherwise returns True."""
        logger.debug('Check execution allowed')
        if not self._execution_allowed.wait(timeout=self.EXECUTION_PAUSED_TIMEOUT_SECONDS):
            logger.error(
                'Execution paused longer than timeout {to}s, raising exception.'.format(
                    to=str(self.EXECUTION_PAUSED_TIMEOUT_SECONDS)))
            raise ExecutionPausedTooLong(self.EXECUTION_PAUSED_TIMEOUT_SECONDS)
        return True

    def _post_command(self, command):
        self._command_queue.put(command)

    def _handle_stop_running_command(self, command):
        self._running = False
        test = self._next_test_case()
        while test is not None:
            test.verdict = Verdict.SKIPPED
            messages.trigger_test_case_skipped(
                self._messagebus, test, 'Skipped because run was aborted')
            logger.info(
                'Test case skipped because run was aborted: {name}: {verdict}'.format(
                    name=test.qualified_name, verdict=test.verdict.name))
            self.run_history.append(test)
            test = self._next_test_case()

        scope = command.current_scope
        while scope != self.runner_scope:
            scope = self.component_factory.exit_scope(scope).scope
        self.component_factory.exit_scope(scope)

    def _handle_next_test_case_command(self, command):
        """
        Schedules the next test case in the run queue for execution.

        If there are more tests available in the run queue, schedule the first
        available test to run. Otherwise, signal the test runner to (stop).
        """

        if self._running and not self._abort:
            next_test_case = self._next_test_case()
            if next_test_case is not None:
                self._post_command(
                    Command(Command.run_test_case, command.current_scope, next_test_case))
            else:
                self._stop_if_no_running_test_cases(command.current_scope)
        else:
            self._stop_if_no_running_test_cases(command.current_scope)

    def _stop_if_no_running_test_cases(self, current_scope):
        with self.running_test_cases.lock:
            if len(self.running_test_cases) == 0:
                self.stop(current_scope)

    def _handle_run_test_case_command(self, command):
        """
        Execute a test case.

        Runs the run method of the current test case. On completion, stores the
        test verdict in the test case object. Following this, schedules exiting
        the test context.
        """
        current_test_case = command.test_case

        def test_completed_callback(future):
            run_result = future.result()

            skip_exception = self._find_parent_exception_of_type(
                run_result.exception, SkipException)
            exception = skip_exception if skip_exception is not None else run_result.exception

            current_test_case.update_verdict(exception, run_result.stacktrace)

            self.run_history.append(current_test_case)

            messages.trigger_test_case_finished(self._messagebus, current_test_case)
            logger.info(
                'Test case completed: {name}: {verdict}'.format(
                    name=current_test_case.full_name, verdict=str(current_test_case.verdict.name)))
            self._post_command(Command(Command.next_test_case, run_result.scope, current_test_case))

        def run_test_case(*args, **kwargs):
            scope = command.current_scope
            try:
                with current_test_case.execution_context:
                    with self.running_test_cases.lock:
                        self.running_test_cases.append(current_test_case)
                    if self._abort:
                        raise SkipException('Skipped because run was aborted')
                    if current_test_case.disabled:
                        raise DisabledException(current_test_case.disabled_message)
                    else:
                        result = self._exit_scopes(scope, current_test_case)
                        scope = result.scope
                        if not result.success:
                            e = self._handle_exit_scopes_fails(current_test_case, result.exceptions)
                            raise SkipException(
                                'Skipping test case due to failures in preparation') from e

                        scope = self._enter_scopes(scope, current_test_case)
                        logger.debug(
                            "Calling test case '{test}' with '{scope}'".format(
                                test=current_test_case.full_name, scope=repr(scope)))

                        try:
                            extra_req = [p.value for p in current_test_case.params if p.is_req]
                            extra_kwargs = {
                                p.key: p.value
                                for p in current_test_case.params if not p.is_req
                            }
                            kwargs.update(extra_kwargs)
                            self.component_factory.call(
                                current_test_case.run, scope, *args, extra_req=extra_req, **kwargs)
                        finally:
                            result = self.component_factory.exit_scope(scope)
                            scope = result.scope
                            if not result.success:
                                self._handle_exit_scopes_fails(current_test_case, result.exceptions)

                        return RunResult(scope, None, None)
            except (Exception, TestCaseAborted) as e:
                try:
                    msg = str(traceback.format_exc())
                except Exception:
                    msg = str(e)
                return RunResult(scope, e, msg)
            finally:
                with self.running_test_cases.lock:
                    self.running_test_cases.remove(current_test_case)

        logger.info('Test case started: {name}'.format(name=current_test_case.full_name))
        messages.trigger_test_case_started(self._messagebus, current_test_case)
        self._submit_to_thread_pool(run_test_case, [test_completed_callback])

    def _find_parent_exception_of_type(self, exception, exception_type):
        """
        Find the parent exception matching the specified type if it exists.

        :param exception: the exception
        :param exception_type: the type of the parent exception to look for
        :return: the parent exception if found or None
        """
        if exception is None:
            return None

        cause = exception.__cause__
        while cause is not None:
            if type(cause) == exception_type:
                return cause

            cause = cause.__cause__
        return None

    def _exit_scopes(self, current_scope, current_test_case):
        cls = current_test_case.test_case_class()
        mod = current_test_case.test_case_module()

        scope = current_scope

        result = ExitScopeResult(None, True, [])
        if scope.name == 'test':
            result.combine(self.component_factory.exit_scope(scope))
            scope = scope.parent

        if scope.name == 'class' and scope.data != cls:
            result.combine(self.component_factory.exit_scope(scope))
            scope = scope.parent

        if scope.name == 'module' and scope.data != mod:
            result.combine(self.component_factory.exit_scope(scope))
            scope = scope.parent

        result.scope = scope
        return result

    def _handle_exit_scopes_fails(self, test_case, exceptions):
        self.abort_run_after_current_test_cases_have_completed()

        msg = 'Error(s) occurred when exiting test case {tc}. Aborting run:\n{msgs}'.format(
            tc=test_case.qualified_name, msgs='\n'.join([str(exc) for exc in exceptions]))

        try:
            # Raising exception to get the full traceback
            if exceptions:
                raise ScopeChangeException(msg) from exceptions[0]
            else:
                raise ScopeChangeException(msg)
        except ScopeChangeException as e:
            logger.debug(str(e), exc_info=True)
            logger.error(str(e))
            self._abort_exceptions.append(e)
            return e

    def _enter_scopes(self, current_scope, current_test_case):
        cls = current_test_case.test_case_class()
        mod = current_test_case.test_case_module()

        scope = current_scope

        if scope.name == 'runner':
            scope = self.component_factory.enter_scope('module', scope, mod)

        if scope.name == 'module' and scope.data == mod and cls is not None:
            scope = self.component_factory.enter_scope('class', scope, cls)

        return self.component_factory.enter_scope('test', scope, current_test_case)

    def _submit_to_thread_pool(self, callable, callbacks=None, *args, **kwargs):
        """
        Submit a task to be executed in the thread pool.

        Optionally, a list of callbacks may be provided. The callbacks are
        executed when the task is task is completed. The callbacks are called
        with a single arguments, the future object that was created when the
        task was submitted to the thread pool.

        The callbacks are always called and are executed by the thread pool.
        """
        callbacks = [] if callbacks is None else callbacks
        future = self.executor.submit(callable, *args, **kwargs)
        for callback in callbacks:
            future.add_done_callback(callback)

    def _calculate_run_verdict(self):
        verdict = Verdict.PASSED

        if self._abort:
            verdict = Verdict.ERROR

        for test_case in self.run_history:
            verdict = verdict.combine(test_case.verdict)

        return verdict

    def _run_failed_message(self):
        if self._abort_exceptions:
            return '\n'.join(
                [
                    ''.join(
                        traceback.format_exception(
                            type(exception), exception, exception.__traceback__))
                    for exception in self._abort_exceptions
                ])
        else:
            return ''

    def _next_test_case(self):
        test_case_definition = self._messagebus.send_request(
            SCHEDULE_NEXT_TEST, SCHEDULER_ENDPOINT).wait(timeout=30)[0].result()
        if test_case_definition is None:
            return None
        else:
            return RunnerTestCase.from_test_case_definition(test_case_definition)


def _async_raise(thread_id, exctype):
    """Raise an exception of the specified type in the target thread."""
    if not inspect.isclass(exctype):
        raise TypeError('Only types can be raised (not instances)')
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread_id), ctypes.py_object(exctype))
    if res == 0:
        raise ValueError('invalid thread id (id={id})'.format(id=thread_id))
    elif res != 1:
        # if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), 0)
        raise SystemError('PyThreadState_SetAsyncExc failed')
    induce_spurious_wakeup_for_all_conditions_associated_with_thread(thread_id)
