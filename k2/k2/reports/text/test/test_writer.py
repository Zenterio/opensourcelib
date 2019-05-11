import datetime
import unittest

from k2.results.results import ResultsCollection, TestCaseResult, TestRunResult
from k2.runner.testcase import Verdict

from .. import writer


class TestWriter(unittest.TestCase):

    def test_verdicts_are_printed(self):
        for verdict in Verdict:
            self.assertIn(
                'tc1 {verdict}'.format(verdict=verdict.name),
                writer.generate_report(results([tc(verdict, 0)]), 'full'))

    def test_format_full_prints_testcases_failures_and_summary(self):
        report = writer.generate_report(results([tc(Verdict.FAILED, 0)]), 'full')
        self.assertIn('Results', report)
        self.assertIn('Failures/Errors', report)
        self.assertIn('Summary', report)

    def test_format_brief_prints_failures_and_summary(self):
        report = writer.generate_report(results([tc(Verdict.FAILED, 0)]), 'brief')
        self.assertNotIn('Results', report)
        self.assertIn('Failures/Errors', report)
        self.assertIn('Summary', report)

    def test_format_summary_only_prints_summary(self):
        report = writer.generate_report(results([tc(Verdict.FAILED, 0)]), 'summary-only')
        self.assertNotIn('Results', report)
        self.assertNotIn('Failures/Errors', report)
        self.assertIn('Summary', report)

    def test_test_result_exception_shown_indented_if_exists(self):
        report = writer.generate_report(
            results([tc(Verdict.FAILED, 0, exception=Exception('Exception Message'))]), 'full')
        self.assertIn('  Exception Message', report)

    def test_test_result_stack_trace_shown_indented_if_exists(self):
        report = writer.generate_report(
            results([tc(Verdict.FAILED, 0, stacktrace='STACKTRACE')]), 'full')
        self.assertIn('  STACKTRACE', report)

    def test_run_verdict_shown_in_results_header(self):
        report = writer.generate_report(
            results([tc(Verdict.FAILED, 0)], run_verdict=Verdict.FAILED), 'full')
        self.assertIn('Results (FAILED)', report)

    def test_run_error_message_shown_if_exists(self):
        report = writer.generate_report(
            results([tc(Verdict.FAILED, 0)], run_verdict=Verdict.FAILED), 'full')
        self.assertIn('RUN ERROR MESSAGE', report)

    def test_owner_shown_if_test_case_has_valid_owner(self):
        report = writer.generate_report(
            results([tc(Verdict.FAILED, 0, owner='owner')], run_verdict=Verdict.FAILED), 'full',
            True)
        self.assertIn('tc1 (Test case owner: owner)', report)

    def test_owner_shown_if_test_run_has_valid_owner_but_test_case_does_not(self):
        report = writer.generate_report(
            results([tc(Verdict.FAILED, 0)], run_verdict=Verdict.FAILED, run_owner='owner'), 'full',
            True)
        self.assertIn('tc1 (Test case owner: owner)', report)

    def test_owner_not_shown_if_no_valid_owner_exists_when_show_owner_is_true(self):
        report = writer.generate_report(
            results([tc(Verdict.FAILED, 0)], run_verdict=Verdict.FAILED), 'full', True)
        self.assertNotIn('(Test case owner: owner)', report)


def results(tcs, run_verdict=Verdict.PASSED, run_owner=None):
    message = ''
    if run_verdict != Verdict.PASSED:
        message = 'RUN ERROR MESSAGE'
    run_result = TestRunResult('Name of Suite', tcs[0].start_time)
    run_result.set_finished(tcs[-1].end_time, run_verdict, message, owner=run_owner)

    return ResultsCollection(tcs, run_result)


def tc(verdict, time_index, exception=None, stacktrace='', owner=None):
    tc = TestCaseResult('tc1', 'a.b.tc1', times[time_index][0])
    tc.set_finished(times[time_index][2], verdict, exception, stacktrace, owner)
    return tc


times = [
    (
        datetime.datetime(2017, 5, 8, 14, 14, 59, 0), '2017-05-08T14:14:59Z',
        datetime.datetime(2017, 5, 8, 14, 15, 17, 34000), '2017-05-08T14:15:17Z', 18034, 18034),
]
