import datetime
import unittest
from unittest.mock import patch

from zaf.builtin.output import OUTPUT_DIR
from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager, InvalidReference

from k2.cmd.run import POST_TEST_RUN, RUN_COMMAND_ENDPOINT
from k2.reports.testng import REPORTS_TESTNG
from k2.results import RESULTS_ENDPOINT, TEST_RESULTS_COLLECTED
from k2.results.results import TestCaseResult
from k2.runner.testcase import Verdict

from ..testng import TestNgReporter


class TestTestNgReporter(unittest.TestCase):

    def test_disabled_does_not_register_to_messages(self):
        config = ConfigManager()
        config.set(REPORTS_TESTNG, False)

        with ExtensionTestHarness(TestNgReporter, config=config) as h:
            assert not h.any_registered_dispatchers(TEST_RESULTS_COLLECTED, RESULTS_ENDPOINT)
            assert not h.any_registered_dispatchers(POST_TEST_RUN, RUN_COMMAND_ENDPOINT)

    def test_enabled_requires_output_dir(self):
        config = ConfigManager()
        config.set(REPORTS_TESTNG, True)

        self.assertRaises(InvalidReference, TestNgReporter, config, {})

    def test_handle_message_creates_result_xml_file(self):
        config = ConfigManager()
        config.set(REPORTS_TESTNG, True)
        config.set(OUTPUT_DIR, 'dir')
        with ExtensionTestHarness(TestNgReporter, endpoints_and_messages={
                RESULTS_ENDPOINT: [TEST_RESULTS_COLLECTED], RUN_COMMAND_ENDPOINT: [POST_TEST_RUN]
        }, config=config) as h:
            with h.patch('k2.reports.testng.writer.write_testng_report') as m, \
                    patch('os.path.exists', return_value=True):
                result = TestCaseResult('name', 'qual_name', datetime.datetime.now())
                result.set_finished(datetime.datetime.now(), Verdict.FAILED, None, '')
                h.trigger_event(TEST_RESULTS_COLLECTED, RESULTS_ENDPOINT, data=[result])
                m.wait_for_call(timeout=1)
                m.assert_called_once_with([result], 'dir/reports/testng/testng-results.xml')
