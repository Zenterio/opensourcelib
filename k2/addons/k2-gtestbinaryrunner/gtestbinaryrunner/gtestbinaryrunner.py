"""
Support for running compiled Google test binaries.

The binaries are assumed to be reasonably standard Google test binaries.
Each binary must either support the default console output format or support
writing an XML report to disk using the --gtest_output=xml option.
"""

import logging
import os
import re
import uuid
from datetime import datetime

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.dispatchers import CallbackDispatcher

from k2.finder.testfinder import RUN_COMMAND
from k2.results.results import TestCaseFinished, TestCaseStarted
from k2.runner import TEST_CASE_FINISHED, TEST_CASE_STARTED
from k2.runner.testcase import Verdict
from multirunner import MULTI_RUNNER_ENABLED, MULTI_RUNNER_ENDPOINT, TEST_SUBRUN

from . import GTEST_BINARY_PATH, GTEST_FILTER, GTEST_SERIAL_ENDMARK, GTEST_TIMEOUT, \
    GTEST_USE_SERIAL, GTEST_XML_REPORT_PATH, GTEST_binaryid

logger = logging.getLogger(get_logger_name('k2', 'gtesbinarytrunner'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='gtestbinaryrunner',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(GTEST_binaryid, required=False, instantiate_on=True),
        ConfigOption(GTEST_BINARY_PATH, required=True),
        ConfigOption(GTEST_TIMEOUT, required=True),
        ConfigOption(GTEST_XML_REPORT_PATH, required=False),
        ConfigOption(GTEST_FILTER, required=False),
        ConfigOption(GTEST_USE_SERIAL, required=False),
        ConfigOption(GTEST_SERIAL_ENDMARK, required=False),
        ConfigOption(MULTI_RUNNER_ENABLED, required=False),
    ],
    activate_on=[MULTI_RUNNER_ENABLED],
    default_enabled=False,
    replaces=['testrunner', 'testscheduler', 'testfinder'],
)
class GtestBinaryRunner(AbstractExtension):

    def __init__(self, config, instances):
        self._entity = instances[GTEST_binaryid]
        self._binary = config.get(GTEST_BINARY_PATH)
        self._timeout = config.get(GTEST_TIMEOUT)
        self._xml_report_path = config.get(GTEST_XML_REPORT_PATH)
        self._filter = config.get(GTEST_FILTER)
        self._messagebus = None
        self._run_dispatcher = None
        self._serial = config.get(GTEST_USE_SERIAL)
        self._endmark = config.get(GTEST_SERIAL_ENDMARK)
        self._create_run()

    def _create_run(self):
        if self._serial:
            can = ['serial']
            params = {'prefix_output': False, 'endmark': self._endmark}
        else:
            can = ['telnet']
            params = {}

        @requires(exec='Exec', can=can, scope='session')
        @requires(messagebus='MessageBus')
        def _run(message, exec, messagebus):
            output = self._run_gtest_binary_on_sut(exec, self._binary, self._filter, params)
            self._log_output(output)
            if self._xml_report_path is not None:
                self._write_gtest_xml_report(self._collect_gtest_xml_report(exec).strip())
                return None
            else:
                return self._parse_gtest_standard_output(messagebus, output)

        self._run = _run

    def register_dispatchers(self, messagebus):
        self._messagebus = messagebus

        self._run_dispatcher = CallbackDispatcher(messagebus, self._run)
        self._run_dispatcher.register(
            message_ids=[TEST_SUBRUN], endpoint_ids=[MULTI_RUNNER_ENDPOINT])

    def destroy(self):
        if self._run_dispatcher is not None:
            self._run_dispatcher.destroy()
            self._run_dispatcher = None

    def _write_gtest_xml_report(self, report):
        os.makedirs(os.path.dirname(self._xml_report_path), exist_ok=True)
        with open(self._xml_report_path, 'w') as f:
            f.write(report)

    def _collect_gtest_xml_report(self, exec):
        try:
            return exec.send_line('cat /dev/shm/report.xml')
        finally:
            exec.send_line('rm /dev/shm/report.xml')

    def _parse_gtest_standard_output(self, messagebus, output):
        run_verdict = Verdict.PASSED
        for name, error_message, verdict in self._parse_test_cases(output):
            id = uuid.uuid1()
            messagebus.trigger_event(
                TEST_CASE_STARTED,
                MULTI_RUNNER_ENDPOINT,
                data=TestCaseStarted(id, name, name, datetime.now()))
            messagebus.trigger_event(
                TEST_CASE_FINISHED,
                MULTI_RUNNER_ENDPOINT,
                data=TestCaseFinished(id, name, datetime.now(), verdict, stacktrace=error_message))
            run_verdict = run_verdict.combine(verdict)
        return run_verdict

    def _parse_test_cases(self, output):
        test_regex = re.compile(
            r"""
                    ^\[\sRUN\s+\]\s(?P<name>\S+)\s*$\s   # start of test and name
                    (?P<message>.*?)?                    # optional multiline message
                    \[\s+(?P<verdict>OK|FAILED)\s+\]     # verdict
                    """, re.VERBOSE | re.MULTILINE | re.DOTALL)

        for match in test_regex.finditer(output):
            yield match.group('name'), match.group('message'), self._map_verdict(
                match.group('verdict'))

    def _log_output(self, output):
        logger.info('----  gtest output begins  ----')
        for line in output.split('\n'):
            logger.info(line)
        logger.info('----  gtest output ends  ----')

    def _run_gtest_binary_on_sut(self, exec, binary, filter, params):
        xml_report_flag = ''
        if self._xml_report_path is not None:
            xml_report_flag = '--gtest_output=xml:/dev/shm/report.xml'
        filter_flag = '' if not filter else '--gtest_filter={filter}'.format(filter=filter)

        command = '{binary} --gtest_color=no --gtest_print_time=0 {filter} {xml_report_flag}'.format(
            binary=binary,
            filter=filter_flag,
            xml_report_flag=xml_report_flag,
        )

        logger.info('Executing gtest: {command}'.format(command=command))
        return exec.send_line(command, timeout=self._timeout, **params)

    def _map_verdict(self, gtest_verdict):
        if gtest_verdict == 'OK':
            return Verdict.PASSED
        elif gtest_verdict == 'FAILED':
            return Verdict.FAILED
        return Verdict.ERROR
