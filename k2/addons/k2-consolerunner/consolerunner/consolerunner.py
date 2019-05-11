"""
Runs shell commands and parses the console output.

Patterns may be provided for which output lines constitute a test failure and
what lines constitute a success. Multiple patterns may be provided.

If a pattern provides a match-group called 'name', that match group will be
used when generating the test report. Otherwise, the entire matched line will
be used in its entierty.
"""

import logging
import re
import uuid
from collections import OrderedDict
from datetime import datetime

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.finder.testfinder import RUN_COMMAND
from k2.results.results import TestCaseFinished, TestCaseStarted
from k2.runner import TEST_CASE_FINISHED, TEST_CASE_STARTED
from k2.runner.testcase import Verdict
from multirunner import MULTI_RUNNER_ENABLED, MULTI_RUNNER_ENDPOINT, TEST_SUBRUN

from . import CONSOLE_BINARY_ERROR_PATTERN, CONSOLE_BINARY_FAILED_PATTERN, \
    CONSOLE_BINARY_IGNORED_PATTERN, CONSOLE_BINARY_PASSED_PATTERN, CONSOLE_BINARY_PATH, \
    CONSOLE_BINARY_PENDING_PATTERN, CONSOLE_BINARY_SKIPPED_PATTERN, CONSOLE_BINARY_TIMEOUT, \
    CONSOLE_binaryid

logger = logging.getLogger(get_logger_name('k2', 'consolerunner'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='consolerunner',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(CONSOLE_binaryid, required=False, instantiate_on=True),
        ConfigOption(CONSOLE_BINARY_PATH, required=True),
        ConfigOption(CONSOLE_BINARY_TIMEOUT, required=True),
        ConfigOption(CONSOLE_BINARY_PASSED_PATTERN, required=False),
        ConfigOption(CONSOLE_BINARY_FAILED_PATTERN, required=False),
        ConfigOption(CONSOLE_BINARY_ERROR_PATTERN, required=False),
        ConfigOption(CONSOLE_BINARY_PENDING_PATTERN, required=False),
        ConfigOption(CONSOLE_BINARY_SKIPPED_PATTERN, required=False),
        ConfigOption(CONSOLE_BINARY_IGNORED_PATTERN, required=False),
        ConfigOption(MULTI_RUNNER_ENABLED, required=False),
    ],
    endpoints_and_messages={},
    activate_on=[MULTI_RUNNER_ENABLED],
    default_enabled=False,
    replaces=['testrunner', 'testscheduler', 'testfinder'],
)
class ConsoleRunner(AbstractExtension):

    def __init__(self, config, instances):
        self._entity = instances.get(CONSOLE_binaryid)
        self._binary = config.get(CONSOLE_BINARY_PATH)
        self._timeout = config.get(CONSOLE_BINARY_TIMEOUT)
        self._patterns = OrderedDict(
            [
                (
                    Verdict.ERROR, [
                        re.compile(pattern)
                        for pattern in config.get(CONSOLE_BINARY_ERROR_PATTERN, [])
                    ]),
                (
                    Verdict.FAILED, [
                        re.compile(pattern)
                        for pattern in config.get(CONSOLE_BINARY_FAILED_PATTERN, [])
                    ]),
                (
                    Verdict.PASSED, [
                        re.compile(pattern)
                        for pattern in config.get(CONSOLE_BINARY_PASSED_PATTERN, [])
                    ]),
                (
                    Verdict.PENDING, [
                        re.compile(pattern)
                        for pattern in config.get(CONSOLE_BINARY_PENDING_PATTERN, [])
                    ]),
                (
                    Verdict.SKIPPED, [
                        re.compile(pattern)
                        for pattern in config.get(CONSOLE_BINARY_SKIPPED_PATTERN, [])
                    ]),
                (
                    Verdict.IGNORED, [
                        re.compile(pattern)
                        for pattern in config.get(CONSOLE_BINARY_IGNORED_PATTERN, [])
                    ]),
            ])

    @callback_dispatcher([TEST_SUBRUN], [MULTI_RUNNER_ENDPOINT])
    @requires(exec='Exec', scope='session')
    @requires(messagebus='MessageBus')
    def run(self, message, exec, messagebus):
        run_verdict = Verdict.PASSED
        for line in exec.send_line(self._binary, timeout=self._timeout).split('\n'):
            for verdict, pattern in self._patterns.items():
                match = _find_match(pattern, line)
                if match:
                    try:
                        test_case_name = match.group('name')
                    except IndexError:
                        test_case_name = line
                    _trigger_testcase_events(test_case_name, verdict, messagebus)
                    run_verdict.combine(verdict)
                    break
        return run_verdict


def _find_match(patterns, line):
    for pattern in patterns:
        match = pattern.match(line)
        if match:
            return match
    return None


def _trigger_testcase_events(name, verdict, messagebus):
    id = uuid.uuid1()
    messagebus.trigger_event(
        TEST_CASE_STARTED,
        MULTI_RUNNER_ENDPOINT,
        data=TestCaseStarted(id, name, name, datetime.now()))
    messagebus.trigger_event(
        TEST_CASE_FINISHED,
        MULTI_RUNNER_ENDPOINT,
        data=TestCaseFinished(id, name, datetime.now(), verdict))
