# flake8: noqa

import datetime
import unittest
from textwrap import dedent

from xmldiff import main

from k2.results.results import ResultsCollection, TestCaseResult, TestRunResult
from k2.runner.testcase import Verdict

from .. import writer


class TestWriter(unittest.TestCase):

    def test_passed(self):
        self.maxDiff = None

        time_index = 0
        self.assertFalse(
            main.diff_texts(
                writer.generate_junit_report(results([tc(Verdict.PASSED,
                                                         time_index)])).encode('utf-8'),
                no_exception(time_index, Verdict.PASSED)))

    def test_failed_test_case_with_exception(self):
        self.maxDiff = None

        time_index = 0
        self.assertFalse(
            main.diff_texts(
                writer.generate_junit_report(
                    results(
                        [tc(Verdict.FAILED, time_index, AssertionError('Message'),
                            'stacktrace')])).encode('utf-8'),
                with_exception(time_index, Verdict.FAILED, 'stacktrace')))

    def test_error_test_case_with_exception(self):
        self.maxDiff = None

        time_index = 0
        self.assertFalse(
            main.diff_texts(
                writer.generate_junit_report(
                    results(
                        [tc(Verdict.ERROR, time_index, AssertionError('Message'),
                            'stacktrace')])).encode('utf-8'),
                with_exception(time_index, Verdict.ERROR, 'stacktrace')))

    def test_skipped(self):
        self.maxDiff = None

        time_index = 0
        self.assertFalse(
            main.diff_texts(
                writer.generate_junit_report(
                    results(
                        [tc(Verdict.SKIPPED, time_index, AssertionError('Message'),
                            'stacktrace')])).encode('utf-8'),
                with_exception(time_index, Verdict.SKIPPED, 'stacktrace')))

    def test_ignored_mapped_to_skip(self):
        self.maxDiff = None

        time_index = 0
        self.assertFalse(
            main.diff_texts(
                writer.generate_junit_report(
                    results(
                        [tc(Verdict.IGNORED, time_index, AssertionError('Message'),
                            'stacktrace')])).encode('utf-8'),
                with_exception(time_index, Verdict.IGNORED, 'stacktrace')))

    def test_params_appended_to_test_case_name(self):
        self.maxDiff = None

        tc = TestCaseResult('tc1', 'a.b.tc1', times[0][0], params=['value1', 'value2'])
        tc.set_finished(times[0][2], Verdict.PASSED, None, '[value1, value2]')
        self.assertFalse(
            main.diff_texts(
                writer.generate_junit_report(results([tc])).encode('utf-8'),
                no_exception(0, Verdict.PASSED, name_suffix='[value1, value2]')))

    def test_multiple_test_cases_with_different_verdicts(self):
        self.maxDiff = None

        tc1 = TestCaseResult('tc1', 'a.b.tc1', times[0][0])
        tc1.set_finished(times[0][2], Verdict.PASSED, None, '')

        tc2 = TestCaseResult('tc2', 'a.b.tc2', times[1][0])
        tc2.set_finished(times[1][2], Verdict.FAILED, AssertionError('Message'), 'stacktrace')

        tc3 = TestCaseResult('tc3', 'a.c.tc3', times[2][0])
        tc3.set_finished(
            times[2][2], Verdict.SKIPPED, AssertionError('test case skipped'), 'stacktrace')

        test_results = results([tc1, tc2, tc3])

        self.assertFalse(
            main.diff_texts(
                writer.generate_junit_report(test_results).encode('utf-8'),
                dedent(
                    f"""\
                <testsuites disabled="0" errors="0" failures="1" tests="3" time="54.102">
                \t<testsuite disabled="0" errors="0" failures="1" file="None" log="None" name="Name of Suite" skipped="1" tests="3" time="54.102" timestamp="{times[0][1]}" url="None">
                \t\t<testcase classname="a.b" name="tc1" status="SUCCESSFUL" time="{times[0][4]}" timestamp="{times[0][1]}"/>
                \t\t<testcase classname="a.b" name="tc2" status="FAILED" time="{times[1][4]}" timestamp="{times[1][1]}">
                \t\t\t<failure message="Message" type="failure">stacktrace</failure>
                \t\t</testcase>
                \t\t<testcase classname="a.c" name="tc3" status="SUCCESSFUL" time="{times[2][4]}" timestamp="{times[2][1]}">
                \t\t\t<skipped message="test case skipped" type="skipped">stacktrace</skipped>
                \t\t</testcase>
                \t</testsuite>
                </testsuites>
                """)))

    def test_run_verdict_mapped_to_test_case(self):
        self.maxDiff = None
        self.assertFalse(
            main.diff_texts(
                writer.generate_junit_report(
                    results([tc(Verdict.PASSED, 0)], run_verdict=Verdict.FAILED)).encode('utf-8'),
                dedent(
                    f"""\
                <testsuites disabled="0" errors="0" failures="1" tests="2" time="18.034">
                \t<testsuite disabled="0" errors="0" failures="1" file="None" log="None" name="Name of Suite" skipped="0" tests="2" time="18.034" timestamp="{times[0][1]}" url="None">
                \t\t<testcase classname="a.b" name="tc1" status="SUCCESSFUL" time="{times[0][4]}" timestamp="{times[0][1]}"/>
                \t\t<testcase classname="Name of Suite" name="Name of Suite" status="FAILED" timestamp="{times[0][1]}">
                \t\t\t<failure message="Message" type="failure"/>
                \t\t</testcase>
                \t</testsuite>
                </testsuites>
                """)))


times = [
    (
        datetime.datetime(2017, 5, 8, 14, 14, 59, 0), '2017-05-08T14:14:59',
        datetime.datetime(2017, 5, 8, 14, 15, 17, 34000), '2017-05-08T14:15:17', '18.034000',
        18.034),
    (
        datetime.datetime(2017, 5, 8, 14, 15, 59, 0), '2017-05-08T14:15:59',
        datetime.datetime(2017, 5, 8, 14, 16, 17, 34000), '2017-05-08T14:16:17', '18.034000',
        78.034),
    (
        datetime.datetime(2017, 5, 8, 14, 16, 59, 0), '2017-05-08T14:16:59',
        datetime.datetime(2017, 5, 8, 14, 17, 17, 34000), '2017-05-08T14:17:17', '18.034000',
        138.034),
]


def no_exception(time_index, verdict, name_suffix=''):
    return dedent(
        f"""\
        <?xml version="1.0" encoding="utf-8"?>
        <testsuites disabled="0" errors="{1 if verdict == Verdict.ERROR else 0}" failures="{1 if verdict == Verdict.FAILED else 0}" tests="1" time="{times[time_index][5]}">
        \t<testsuite disabled="0" errors="{1 if verdict == Verdict.ERROR else 0}" failures="{1 if verdict == Verdict.FAILED else 0}" file="None" log="None" name="Name of Suite" skipped="{1 if verdict in [Verdict.SKIPPED, Verdict.ERROR] else 0}" tests="1" time="{times[time_index][5]}" timestamp="{times[time_index][1]}" url="None">
        \t\t<testcase classname="a.b" name="tc1{name_suffix}" status="{'FAILED' if verdict in [Verdict.FAILED, Verdict.ERROR] else 'SUCCESSFUL'}" time="{times[time_index][4]}" timestamp="{times[time_index][1]}"/>
        \t</testsuite>
        </testsuites>
        """).encode('utf-8')


def with_exception(time_index, verdict, stacktrace):
    return dedent(
        f"""\
        <?xml version="1.0" encoding="utf-8"?>
        <testsuites disabled="0" errors="{1 if verdict == Verdict.ERROR else 0}" failures="{1 if verdict == Verdict.FAILED else 0}" tests="1" time="{times[time_index][5]}">
        \t<testsuite disabled="0" errors="{1 if verdict == Verdict.ERROR else 0}" failures="{1 if verdict == Verdict.FAILED else 0}" file="None" log="None" name="Name of Suite" skipped="{1 if verdict in [Verdict.SKIPPED, Verdict.IGNORED] else 0}" tests="1" time="{times[time_index][5]}" timestamp="{times[time_index][1]}" url="None">
        \t\t<testcase classname="a.b" name="tc1" status="{'FAILED' if verdict in [Verdict.FAILED, Verdict.ERROR] else 'SUCCESSFUL'}" time="{times[time_index][4]}" timestamp="{times[time_index][1]}">
        \t\t\t<{'failure' if verdict == Verdict.FAILED else 'error' if verdict == Verdict.ERROR else 'skipped'} message="Message" type="{'failure' if verdict == Verdict.FAILED else 'error' if verdict == Verdict.ERROR else 'skipped'}">{stacktrace}</{'failure' if verdict == Verdict.FAILED else 'error' if verdict == Verdict.ERROR else 'skipped'}>
        \t\t</testcase>
        \t</testsuite>
        </testsuites>
        """).encode('utf-8')


def results(tcs, suite_name='Name of Suite', run_verdict=Verdict.PASSED):
    message = None
    if run_verdict != Verdict.PASSED:
        message = dedent("Message")

    run_result = TestRunResult(suite_name, tcs[0].start_time)
    run_result.set_finished(tcs[-1].end_time, run_verdict, message)

    return ResultsCollection(tcs, run_result)


def tc(verdict, time_index, exception=None, stacktrace=''):
    tc = TestCaseResult('tc1', 'a.b.tc1', times[time_index][0])
    tc.set_finished(times[time_index][2], verdict, exception, stacktrace)
    return tc
