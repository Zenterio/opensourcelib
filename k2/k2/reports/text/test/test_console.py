import datetime
import unittest

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2.cmd.run import POST_TEST_RUN, RUN_COMMAND_ENDPOINT
from k2.reports.text import REPORTS_TEXT
from k2.reports.text.text import TextReporter
from k2.results import RESULTS_ENDPOINT, TEST_RESULTS_COLLECTED
from k2.results.results import TestCaseResult
from k2.runner.testcase import Verdict


class TestTextReporter(unittest.TestCase):

    def test_disabled_does_not_register_to_messages(self):
        with ExtensionTestHarness(TextReporter, config=create_config()) as h:
            assert not h.any_registered_dispatchers(TEST_RESULTS_COLLECTED, RESULTS_ENDPOINT)
            assert not h.any_registered_dispatchers(POST_TEST_RUN, RUN_COMMAND_ENDPOINT)

    def test_handle_message_calls_write_report(self):
        with ExtensionTestHarness(TextReporter, endpoints_and_messages={
                RESULTS_ENDPOINT: [TEST_RESULTS_COLLECTED], RUN_COMMAND_ENDPOINT: [POST_TEST_RUN]
        }, config=create_config(reports_text=True)) as h:
            with h.patch('k2.reports.text.writer.write_report') as m:
                result = TestCaseResult('name', 'qual_name', datetime.datetime.now())
                result.set_finished(datetime.datetime.now(), Verdict.FAILED, None, '')
                h.trigger_event(TEST_RESULTS_COLLECTED, RESULTS_ENDPOINT, data=[result])
                m.wait_for_call(timeout=1)
                m.assert_called_once_with([result], {'-'}, 'full', False)


def create_config(reports_text=False):
    config = ConfigManager()
    config.set(REPORTS_TEXT, reports_text)

    return config
