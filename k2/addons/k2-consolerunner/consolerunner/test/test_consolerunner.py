from queue import Empty
from textwrap import dedent
from unittest import TestCase
from unittest.mock import Mock

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import LocalMessageQueue

from k2.runner import TEST_CASE_FINISHED, TEST_CASE_STARTED, TEST_RUN_FINISHED, TEST_RUN_STARTED
from k2.runner.testcase import Verdict
from multirunner import MULTI_RUNNER_ENDPOINT, TEST_SUBRUN

from .. import CONSOLE_BINARY_FAILED_PATTERN, CONSOLE_BINARY_PASSED_PATTERN, CONSOLE_BINARY_PATH, \
    CONSOLE_BINARY_TIMEOUT, CONSOLE_binaryid
from ..consolerunner import ConsoleRunner


class TestConsoleRunner(TestCase):

    @staticmethod
    def create_harness(success_patterns=None, failure_patterns=None):
        entity = 'binaryid'
        config = ConfigManager()
        config.set(CONSOLE_binaryid, [entity])
        config.set(CONSOLE_BINARY_PATH, 'binary_path', entity=entity)
        config.set(CONSOLE_BINARY_TIMEOUT, 3, entity=entity)

        if success_patterns is not None:
            config.set(CONSOLE_BINARY_PASSED_PATTERN, success_patterns, entity=entity)

        if failure_patterns is not None:
            config.set(CONSOLE_BINARY_FAILED_PATTERN, failure_patterns, entity=entity)

        return ExtensionTestHarness(
            ConsoleRunner,
            endpoints_and_messages={
                MULTI_RUNNER_ENDPOINT: [
                    TEST_RUN_STARTED, TEST_RUN_FINISHED, TEST_CASE_STARTED, TEST_CASE_FINISHED,
                    TEST_SUBRUN
                ]
            },
            config=config,
        )

    def test_creating_an_instance(self):
        with TestConsoleRunner.create_harness() as harness:
            assert harness.extension._entity == 'binaryid'
            assert harness.extension._binary == 'binary_path'
            assert harness.extension._timeout == 3
            assert harness.extension._patterns == {
                Verdict.PASSED: [],
                Verdict.FAILED: [],
                Verdict.ERROR: [],
                Verdict.PENDING: [],
                Verdict.SKIPPED: [],
                Verdict.IGNORED: [],
            }

    def test_running_a_binary_with_no_patterns(self):
        with TestConsoleRunner.create_harness() as harness:
            binary_output = dedent(
                """
                   some text
                   some more text
                   """)
            exec = Mock()
            exec.send_line.return_value = binary_output

            with LocalMessageQueue(harness.messagebus, [TEST_CASE_FINISHED]) as queue:
                harness.extension.run(message=None, exec=exec, messagebus=harness.messagebus)
                self.assertRaises(Empty, queue.get_nowait)

    def test_running_a_binary_with_matching_failure_patterns(self):
        failure_patterns = ['failure_a', 'failure_b']
        with TestConsoleRunner.create_harness(failure_patterns=failure_patterns) as harness:
            binary_output = dedent(
                """
                   failure_a
                   some text
                   some more text
                   failure_b
                   """)
            exec = Mock()
            exec.send_line.return_value = binary_output

            with LocalMessageQueue(harness.messagebus, [TEST_CASE_FINISHED]) as queue:
                harness.extension.run(message=None, exec=exec, messagebus=harness.messagebus)
                failure_a_message = queue.get(timeout=1)
                assert failure_a_message.data.name == 'failure_a'
                assert failure_a_message.data.verdict == Verdict.FAILED
                failure_b_message = queue.get(timeout=1)
                assert failure_b_message.data.name == 'failure_b'
                assert failure_b_message.data.verdict == Verdict.FAILED

    def test_running_a_binary_with_matching_success_patterns(self):
        success_patterns = ['success_a', 'success_b']
        with TestConsoleRunner.create_harness(success_patterns=success_patterns) as harness:
            binary_output = dedent(
                """
                   success_a
                   some text
                   some more text
                   success_b
                   """)
            exec = Mock()
            exec.send_line.return_value = binary_output

            with LocalMessageQueue(harness.messagebus, [TEST_CASE_FINISHED]) as queue:
                harness.extension.run(message=None, exec=exec, messagebus=harness.messagebus)
                success_a_message = queue.get(timeout=1)
                assert success_a_message.data.name == 'success_a'
                assert success_a_message.data.verdict == Verdict.PASSED
                success_b_message = queue.get(timeout=1)
                assert success_b_message.data.name == 'success_b'
                assert success_b_message.data.verdict == Verdict.PASSED

    def test_running_a_binary_with_mixed_results(self):
        success_patterns = ['success']
        failure_patterns = ['failure']
        with TestConsoleRunner.create_harness(success_patterns, failure_patterns) as harness:
            binary_output = dedent(
                """
                   success
                   some text
                   some more text
                   failure
                   """)
            exec = Mock()
            exec.send_line.return_value = binary_output

            with LocalMessageQueue(harness.messagebus, [TEST_CASE_FINISHED]) as queue:
                harness.extension.run(message=None, exec=exec, messagebus=harness.messagebus)
                success_message = queue.get(timeout=1)
                assert success_message.data.name == 'success'
                assert success_message.data.verdict == Verdict.PASSED
                failure_message = queue.get(timeout=1)
                assert failure_message.data.name == 'failure'
                assert failure_message.data.verdict == Verdict.FAILED

    def test_failure_is_reported_if_both_success_and_failure_patterns_match(self):
        success_patterns = ['pattern']
        failure_patterns = ['pattern']
        with TestConsoleRunner.create_harness(success_patterns, failure_patterns) as harness:
            binary_output = dedent(
                """
                   some text
                   pattern
                   some more text
                   """)
            exec = Mock()
            exec.send_line.return_value = binary_output

            with LocalMessageQueue(harness.messagebus, [TEST_CASE_FINISHED]) as queue:
                harness.extension.run(message=None, exec=exec, messagebus=harness.messagebus)
                message = queue.get(timeout=1)
                assert message.data.name == 'pattern'
                assert message.data.verdict == Verdict.FAILED

    def test_if_a_matchgroup_called_name_is_provided_it_is_used_as_the_test_case_name(self):
        success_patterns = [r'my long (?P<name>\w+) case name']
        with TestConsoleRunner.create_harness(success_patterns) as harness:
            binary_output = dedent(
                """
                   my long test case name
                   """)
            exec = Mock()
            exec.send_line.return_value = binary_output

            with LocalMessageQueue(harness.messagebus, [TEST_CASE_FINISHED]) as queue:
                harness.extension.run(message=None, exec=exec, messagebus=harness.messagebus)
                message = queue.get(timeout=1)
                assert message.data.name == 'test'
