"""
The default K2 test runner that runs a suite of tests and sends out messages with results for each test.

The runner support parallel execution by setting the :ref:`option-parallel.workers` option to greater than one.
When running parallel test cases all components on runner and session scope need to be thread safe.
Components on shorter scopes will be instantiated uniquely for each test thread.

Example flow of events for Manager:
===================================
    .. uml::

        participant "Runcommand" as run
        participant "SutEvents" as sutevents
        participant "TestRunnerManager" as extension
        participant "TestRunner" as runner

        run -> extension: TEST_RUN
        activate extension
        extension -> runner: init()
        extension -> runner: run()
        activate runner
        runner -> runner: //start execution//
        activate runner #Gray
        sutevents -> extension: SUT_RESET_STARTED
        extension -> runner: pause_execution()
        deactivate runner
        sutevents -> extension: SUT_RESET_DONE
        extension -> runner: resume_execution()
        activate runner #Gray
        runner -> runner: //no more tests to run//
        deactivate runner
        runner -> extension: run() returns
        deactivate runner

        run <- extension
        deactivate extension

Example flow of events for TestRunner:
======================================

    .. uml::

        participant "TestRunnerManager" as extension
        participant "TestRunner" as runner
        participant "Scheduler" as scheduler
        participant "TestResults" as result


        activate extension
        extension -> runner: init()
        extension -> runner: run()
        activate runner
        runner -> runner: //next test case//
        runner -> runner: //start execution//
        activate runner #Gray

        runner -> scheduler: //SCHEDULE_NEXT_TEST//
        runner -> runner: //execute test case//
        runner -> result: TEST_CASE_FINISHED
        runner -> runner: //next test case//
        runner -> scheduler: //SCHEDULE_NEXT_TEST//


        extension -> runner: pause_execution()
        deactivate runner
        extension -> runner: resume_execution()
        activate runner #Gray
        runner -> runner: //execute test case//
        runner -> result: TEST_CASE_FINISHED
        runner -> runner: //no more tests to run//
        deactivate runner
        runner -> extension: run() returns
        deactivate runner

        deactivate extension
"""

import logging
import threading

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2 import ABORT, CRITICAL_ABORT
from k2.cmd.run import RUN_COMMAND, TEST_RUN
from k2.runner import ABORT_TEST_CASE_REQUEST, EXTENSION_NAME, RUNNER_PARALLEL_WORKERS, messages
from k2.runner.runner import TestRunner
from k2.sut import SUT_RESET_DONE, SUT_RESET_STARTED

from . import RUNNER_SUITE_NAME

logger = logging.getLogger(get_logger_name('k2', EXTENSION_NAME, 'manager'))
logger.addHandler(logging.NullHandler())


class AbortedBeforeStartException(Exception):
    pass


@CommandExtension(
    name=EXTENSION_NAME,
    config_options=[
        ConfigOption(RUNNER_SUITE_NAME, required=True),
        ConfigOption(RUNNER_PARALLEL_WORKERS, required=True),
    ],
    extends=[RUN_COMMAND],
    endpoints_and_messages=messages.runner_endpoint_with_messages())
class TestRunnerManager(AbstractExtension):
    """Run a test suite as a callback on the RUN_COMMAND TEST_RUN event."""

    def __init__(self, config, instances):
        self._suite_name = config.get(RUNNER_SUITE_NAME)
        self._external_message_lock = threading.Lock()
        self._runner = None
        self._resetting_entities = set()
        self._parallel_workers = config.get(RUNNER_PARALLEL_WORKERS)
        self._aborted = False

    @callback_dispatcher([ABORT, CRITICAL_ABORT])
    def abort_message_handler(self, message):
        with self._external_message_lock:
            self._aborted = True
            if message.message_id == ABORT:
                self.abort()
            elif message.message_id == CRITICAL_ABORT:
                self.critical_abort()

    def abort(self):
        if self._runner:
            self._runner.abort_run_after_current_test_cases_have_completed()
        else:
            logger.warning('Abort received in testrunner but no runner instance is active')

    def critical_abort(self):
        if self._runner:
            self._runner.abort_run_immediately()
        else:
            logger.warning('Critical abort received in testrunner but no runner instance is active')

    @callback_dispatcher([SUT_RESET_STARTED, SUT_RESET_DONE], optional=True)
    def sut_reset_message_handler(self, message):
        with self._external_message_lock:
            if message.message_id == SUT_RESET_STARTED:
                self.pause_test_execution(message.entity)
            if message.message_id == SUT_RESET_DONE:
                self.resume_test_execution(message.entity)

    def pause_test_execution(self, entity):
        """
        Pause the test runner.

        :param entity: entity being reset.
        """
        self._resetting_entities.add(entity)
        if self._runner:
            logger.debug(
                'Pausing test execution until SUT {entity} reset done'.format(entity=entity))
            self._runner.pause_execution()

    def resume_test_execution(self, entity):
        """
        Resume the test runner.

        :param entity: entity being reset.
        """
        self._resetting_entities.discard(entity)
        if self._resetting_entities:
            logger.debug('Still waiting for SUTs to finish resetting')
        else:
            logger.debug('SUT {entity} done resetting'.format(entity=entity))
            if self._runner:
                logger.debug('Resuming test execution')
                self._runner.resume_execution()

    @callback_dispatcher([TEST_RUN])
    @requires(component_factory='ComponentFactory')
    @requires(messagebus='MessageBus')
    def run(self, message, component_factory, messagebus):
        with self._external_message_lock:
            if not self._aborted:
                self._runner = TestRunner(
                    messagebus, component_factory, self._suite_name, message.data.parent_scope)
            else:
                raise AbortedBeforeStartException('The test run was aborted before it was started')

        self._runner.run(self._parallel_workers)
        self._runner = None

    @callback_dispatcher([ABORT_TEST_CASE_REQUEST])
    def _handle_abort_test_case_request(self, message):
        with self._external_message_lock:
            if self._runner:
                self._runner.abort_test_case(message.data)
            else:
                logger.warning(
                    'Test case abort received in testrunner but no runner instance is active')
