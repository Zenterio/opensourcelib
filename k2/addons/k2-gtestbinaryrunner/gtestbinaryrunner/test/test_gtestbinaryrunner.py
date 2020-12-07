from textwrap import dedent
from unittest import TestCase
from unittest.mock import Mock, call

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import LocalMessageQueue

from k2.runner import TEST_CASE_FINISHED, TEST_CASE_STARTED, TEST_RUN_FINISHED, TEST_RUN_STARTED
from k2.runner.testcase import Verdict
from multirunner import MULTI_RUNNER_ENDPOINT, TEST_SUBRUN

from .. import GTEST_BINARY_PATH, GTEST_FILTER, GTEST_XML_REPORT_PATH, GTEST_binaryid
from ..gtestbinaryrunner import GtestBinaryRunner


class TestGtestBinaryRunner(TestCase):

    @staticmethod
    def create_harness(xml_report_path=None):
        config = ConfigManager()
        entity = 'gtest'
        config.set(GTEST_binaryid, ['gtest'])
        config.set(GTEST_FILTER, 'filter', entity=entity)
        config.set(GTEST_BINARY_PATH, 'path/to/binary', entity=entity)
        config.set(GTEST_XML_REPORT_PATH, xml_report_path, entity=entity)

        return ExtensionTestHarness(
            GtestBinaryRunner,
            endpoints_and_messages={
                MULTI_RUNNER_ENDPOINT: [
                    TEST_SUBRUN,
                    TEST_RUN_STARTED,
                    TEST_RUN_FINISHED,
                    TEST_CASE_STARTED,
                    TEST_CASE_FINISHED,
                ]
            },
            config=config)

    def test_parsing_multiple_passing_tests(self):
        with TestGtestBinaryRunner.create_harness() as harness:
            gtest_output = dedent(
                """
                [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                [       OK ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/1
                [       OK ] SbCryptographyTransform/Aes.SunnyDayIdentity/1
                [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/2
                [       OK ] SbCryptographyTransform/Aes.SunnyDayIdentity/2
                """)

            results = list(harness.extension._parse_test_cases(gtest_output))
            self.assertEqual(
                results, [
                    ('SbCryptographyTransform/Aes.SunnyDayIdentity/0', '', Verdict.PASSED),
                    ('SbCryptographyTransform/Aes.SunnyDayIdentity/1', '', Verdict.PASSED),
                    ('SbCryptographyTransform/Aes.SunnyDayIdentity/2', '', Verdict.PASSED),
                ])

    def test_parsing_multiple_failing_tests(self):
        with TestGtestBinaryRunner.create_harness() as harness:
            gtest_output = dedent(
                """
                [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                [  FAILED  ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/1
                [  FAILED  ] SbCryptographyTransform/Aes.SunnyDayIdentity/1
                [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/2
                [  FAILED  ] SbCryptographyTransform/Aes.SunnyDayIdentity/2
                """)

            results = list(harness.extension._parse_test_cases(gtest_output))
            self.assertEqual(
                results, [
                    ('SbCryptographyTransform/Aes.SunnyDayIdentity/0', '', Verdict.FAILED),
                    ('SbCryptographyTransform/Aes.SunnyDayIdentity/1', '', Verdict.FAILED),
                    ('SbCryptographyTransform/Aes.SunnyDayIdentity/2', '', Verdict.FAILED),
                ])

    def test_parsing_multiple_test_cases_with_different_verdicts(self):
        with TestGtestBinaryRunner.create_harness() as harness:
            gtest_output = dedent(
                """
                  [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                  [       OK ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                  [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/1
                  [  FAILED  ] SbCryptographyTransform/Aes.SunnyDayIdentity/1
                  [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/2
                  [       OK ] SbCryptographyTransform/Aes.SunnyDayIdentity/2
                  """)

            results = list(harness.extension._parse_test_cases(gtest_output))
            self.assertEqual(
                results, [
                    ('SbCryptographyTransform/Aes.SunnyDayIdentity/0', '', Verdict.PASSED),
                    ('SbCryptographyTransform/Aes.SunnyDayIdentity/1', '', Verdict.FAILED),
                    ('SbCryptographyTransform/Aes.SunnyDayIdentity/2', '', Verdict.PASSED),
                ])

    def test_parsing_failing_test_case_with_messages(self):
        with TestGtestBinaryRunner.create_harness() as harness:
            gtest_output = dedent(
                """
                  [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                  this
                  is
                  an
                  error
                  message
                  [  FAILED  ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                  [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/1
                  [       OK ] SbCryptographyTransform/Aes.SunnyDayIdentity/1
                  """)

            results = list(harness.extension._parse_test_cases(gtest_output))
            self.assertEqual(
                results, [
                    (
                        'SbCryptographyTransform/Aes.SunnyDayIdentity/0',
                        dedent(
                            """\
                         this
                         is
                         an
                         error
                         message
                         """), Verdict.FAILED),
                    ('SbCryptographyTransform/Aes.SunnyDayIdentity/1', '', Verdict.PASSED),
                ])

    def test_passing_test_translated_to_test_events(self):
        with TestGtestBinaryRunner.create_harness() as harness:
            gtest_output = dedent(
                """
                  [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                  [       OK ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                  """)
            exec = Mock()
            exec.send_line.return_value = gtest_output

            events = [TEST_CASE_STARTED, TEST_CASE_FINISHED]
            with LocalMessageQueue(harness.messagebus, events) as queue:
                harness.extension._run(None, exec=exec, messagebus=harness.messagebus)
                self.assertEqual(queue.get(timeout=1).message_id, TEST_CASE_STARTED)
                test_case_finished_message = queue.get(timeout=1)
                self.assertEqual(test_case_finished_message.message_id, TEST_CASE_FINISHED)
                self.assertEqual(test_case_finished_message.data.verdict, Verdict.PASSED)

    def test_failed_test_translated_to_test_events(self):
        with TestGtestBinaryRunner.create_harness() as harness:
            gtest_output = dedent(
                """
                   [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                   [  FAILED  ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                   """)
            exec = Mock()
            exec.send_line.return_value = gtest_output

            events = [TEST_CASE_STARTED, TEST_CASE_FINISHED]
            with LocalMessageQueue(harness.messagebus, events) as queue:
                harness.extension._run(message=None, exec=exec, messagebus=harness.messagebus)
                self.assertEqual(queue.get(timeout=1).message_id, TEST_CASE_STARTED)
                test_case_finished_message = queue.get(timeout=1)
                self.assertEqual(test_case_finished_message.message_id, TEST_CASE_FINISHED)
                self.assertEqual(test_case_finished_message.data.verdict, Verdict.FAILED)

    def test_message_included_in_test_case_finished_as_stacktrace(self):
        with TestGtestBinaryRunner.create_harness() as harness:
            gtest_output = dedent(
                """
                   [ RUN      ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                   this
                   is
                   a
                   message
                   [  FAILED  ] SbCryptographyTransform/Aes.SunnyDayIdentity/0
                   """)
            exec = Mock()
            exec.send_line.return_value = gtest_output

            with LocalMessageQueue(harness.messagebus, [TEST_CASE_FINISHED]) as queue:
                harness.extension._run(message=None, exec=exec, messagebus=harness.messagebus)
                test_case_finished_message = queue.get(timeout=1)
                self.assertEqual(test_case_finished_message.message_id, TEST_CASE_FINISHED)
                self.assertEqual(
                    test_case_finished_message.data.stacktrace,
                    dedent(
                        """\
                        this
                        is
                        a
                        message
                        """))

    def test_interaction_with_gtest_when_writing_xml_report(self):
        with TestGtestBinaryRunner.create_harness('./myreport.xml') as harness:
            harness.extension._write_gtest_xml_report = Mock()
            exec = Mock()
            exec.send_line.return_value = 'hello I am a gtest binary'

            harness.extension._run(message=None, exec=exec, messagebus=harness.messagebus)
            calls = exec.send_line.call_args_list
            assert '--gtest_output=xml:/dev/shm/report.xml' in str(calls[0])
            assert call('cat /dev/shm/report.xml') == calls[1]
            assert call('rm /dev/shm/report.xml') == calls[2]
            harness.extension._write_gtest_xml_report.assert_called_once_with(
                exec.send_line.return_value)
