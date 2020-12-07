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

        time_index = 1
        self.assertFalse(
            main.diff_texts(
                writer.generate_testng_report(results([tc(Verdict.PASSED, time_index)])),
                no_exception(time_index, 'PASS')))

    def test_failed_test_case_with_exception(self):
        self.maxDiff = None

        time_index = 1
        self.assertFalse(
            main.diff_texts(
                writer.generate_testng_report(
                    results(
                        [
                            tc(
                                Verdict.FAILED, time_index, AssertionError('assert failed'),
                                'stacktrace')
                        ])), with_exception(time_index, 'FAIL', 'stacktrace')))

    def test_error_mapped_to_fail(self):
        self.maxDiff = None

        time_index = 2
        self.assertFalse(
            main.diff_texts(
                writer.generate_testng_report(
                    results(
                        [
                            tc(
                                Verdict.ERROR, time_index, AssertionError('assert failed'),
                                'stacktrace')
                        ])), with_exception(time_index, 'FAIL', 'stacktrace')))

    def test_skipped(self):
        self.maxDiff = None

        time_index = 0
        self.assertFalse(
            main.diff_texts(
                writer.generate_testng_report(
                    results(
                        [
                            tc(
                                Verdict.SKIPPED, time_index, AssertionError('assert failed'),
                                'stacktrace')
                        ])), with_exception(time_index, 'SKIP', 'stacktrace')))

    def test_ignored_mapped_to_skip(self):
        self.maxDiff = None

        time_index = 2
        self.assertFalse(
            main.diff_texts(
                writer.generate_testng_report(
                    results(
                        [
                            tc(
                                Verdict.IGNORED, time_index, AssertionError('assert failed'),
                                'stacktrace')
                        ])), with_exception(time_index, 'SKIP', 'stacktrace')))

    def test_pending_mapped_to_fail(self):
        self.maxDiff = None

        time_index = 2
        self.assertFalse(
            main.diff_texts(
                writer.generate_testng_report(
                    results(
                        [
                            tc(
                                Verdict.PENDING, time_index, AssertionError('assert failed'),
                                'stacktrace')
                        ])), with_exception(time_index, 'FAIL', 'stacktrace')))

    def test_test_case_with_params(self):
        self.maxDiff = None

        tc = TestCaseResult('tc1', 'a.b.tc1', times[0][0], params=['value1', 'value2'])
        tc.set_finished(times[0][2], Verdict.PASSED, None, '')

        self.assertFalse(
            main.diff_texts(
                writer.generate_testng_report(results([tc])),
                dedent(
                    """\
                <?xml version="1.0" encoding="utf-8"?>
                <testng-results version="1.0">
                    <reporter-output/>
                    <suite duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="Name of Suite" started-at="2017-05-08T14:14:59Z">
                        <groups/>
                        <test duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="Name of Suite" started-at="2017-05-08T14:14:59Z">
                            <class name="a.b">
                                <test-method duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="tc1" signature="a.b.tc1" started-at="2017-05-08T14:14:59Z" status="PASS">
                                    <params>
                                        <param index="0">
                                            <value>
                <![CDATA[value1]]>                                \


                                            </value>
                                        </param>
                                        <param index="1">
                                            <value>
                <![CDATA[value2]]>                                \


                                            </value>
                                        </param>
                                    </params>
                                </test-method>
                            </class>
                        </test>
                    </suite>
                </testng-results>
                """).encode('utf-8')))

    def test_multiple_test_cases_with_different_verdicts(self):
        self.maxDiff = None

        tc1 = TestCaseResult('tc1', 'a.b.tc1', times[0][0])
        tc1.set_finished(times[0][2], Verdict.PASSED, None, '')

        tc2 = TestCaseResult('tc2', 'a.b.tc2', times[1][0])
        tc2.set_finished(times[1][2], Verdict.FAILED, AssertionError('assert failed'), 'stacktrace')

        tc3 = TestCaseResult('tc3', 'a.c.tc3', times[2][0])
        tc3.set_finished(
            times[2][2], Verdict.SKIPPED, AssertionError('test case skipped'), 'stacktrace')

        test_results = results([tc1, tc2, tc3])

        self.assertFalse(
            main.diff_texts(
                writer.generate_testng_report(test_results),
                dedent(
                    """\
            <?xml version="1.0" encoding="utf-8"?>
            <testng-results version="1.0">
                <reporter-output/>
                <suite duration-ms="138034" finished-at="2017-05-08T14:17:17Z" name="Name of Suite" started-at="2017-05-08T14:14:59Z">
                    <groups/>
                    <test duration-ms="138034" finished-at="2017-05-08T14:17:17Z" name="Name of Suite" started-at="2017-05-08T14:14:59Z">
                        <class name="a.b">
                            <test-method duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="tc1" signature="a.b.tc1" started-at="2017-05-08T14:14:59Z" status="PASS"/>
                            <test-method duration-ms="18034" finished-at="2017-05-08T14:16:17Z" name="tc2" signature="a.b.tc2" started-at="2017-05-08T14:15:59Z" status="FAIL">
                                <exception class="AssertionError">
                                    <message>
            <![CDATA[assert failed.]]>                            \


                                    </message>
                                    <full-stacktrace>
            <![CDATA[AssertionError: assert failed.
            stacktrace]]>                            \


                                    </full-stacktrace>
                                </exception>
                                <reporter-output/>
                            </test-method>
                        </class>
                        <class name="a.c">
                            <test-method duration-ms="18034" finished-at="2017-05-08T14:17:17Z" name="tc3" signature="a.c.tc3" started-at="2017-05-08T14:16:59Z" status="SKIP">
                                <exception class="AssertionError">
                                    <message>
            <![CDATA[test case skipped.]]>                            \


                                    </message>
                                    <full-stacktrace>
            <![CDATA[AssertionError: test case skipped.
            stacktrace]]>                            \


                                    </full-stacktrace>
                                </exception>
                                <reporter-output/>
                            </test-method>
                        </class>
                    </test>
                </suite>
            </testng-results>
            """).encode('utf-8')))

    def test_run_verdict_mapped_to_test_case(self):
        self.maxDiff = None
        self.assertFalse(
            main.diff_texts(
                writer.generate_testng_report(
                    results([tc(Verdict.PASSED, 0)], run_verdict=Verdict.FAILED)),
                dedent(
                    """\
                <?xml version="1.0" encoding="utf-8"?>
                <testng-results version="1.0">
                    <reporter-output/>
                    <suite duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="Name of Suite" started-at="2017-05-08T14:14:59Z">
                        <groups/>
                        <test duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="Name of Suite" started-at="2017-05-08T14:14:59Z">
                            <class name="a.b">
                                <test-method duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="tc1" signature="a.b.tc1" started-at="2017-05-08T14:14:59Z" status="PASS"/>
                            </class>
                            <class name="Name of Suite">
                                <test-method duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="Name of Suite" signature="Name of Suite" started-at="2017-05-08T14:14:59Z" status="FAIL">
                                    <exception class="str">
                                        <message>
                <![CDATA[A
                multiline
                error
                message
                .]]>                            \n\
                \n\
                                        </message>
                                        <full-stacktrace>
                <![CDATA[str: A
                multiline
                error
                message
                .
                ]]>                            \n\
                \n\
                                        </full-stacktrace>
                                    </exception>
                                    <reporter-output/>
                                </test-method>
                            </class>
                        </test>
                    </suite>
                </testng-results>
                """).encode('utf-8')))

    def test_test_case_with_owner(self):
        self.maxDiff = None

        tc = TestCaseResult('tc1', 'a.b.tc1', times[0][0])
        tc.set_finished(
            times[0][2],
            Verdict.PASSED,
            exception=None,
            stacktrace=None,
            owner=('Owner <owner@zenterio.com>'))

        self.assertFalse(
            main.diff_texts(
                writer.generate_testng_report(results([tc])),
                dedent(
                    """\
                <?xml version="1.0" encoding="utf-8"?>
                <testng-results version="1.0">
                    <reporter-output/>
                    <suite duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="Name of Suite" started-at="2017-05-08T14:14:59Z">
                        <groups/>
                        <test duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="Name of Suite" started-at="2017-05-08T14:14:59Z">
                            <class name="a.b">
                                <test-method description="Test case owner: Owner &lt;owner@zenterio.com&gt; (Please contact the owner if you need assistance with trouble-shooting.)" duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="tc1" signature="a.b.tc1" started-at="2017-05-08T14:14:59Z" status="PASS"/>
                            </class>
                        </test>
                    </suite>
                </testng-results>
                """).encode('utf-8')))

    def test_test_case_with_colons(self):
        self.maxDiff = None

        tc = TestCaseResult('a:b', 'b:c', times[0][0])
        tc.set_finished(times[0][2], Verdict.PASSED, exception=None, stacktrace=None)

        self.assertFalse(
            main.diff_texts(
                writer.generate_testng_report(results([tc], suite_name='c:d')),
                dedent(
                    """\
                <?xml version="1.0" encoding="utf-8"?>
                <testng-results version="1.0">
                    <reporter-output/>
                    <suite duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="cd" started-at="2017-05-08T14:14:59Z">
                        <groups/>
                        <test duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="cd" started-at="2017-05-08T14:14:59Z">
                            <class name="ab">
                                <test-method duration-ms="18034" finished-at="2017-05-08T14:15:17Z" name="bc" signature="bc" started-at="2017-05-08T14:14:59Z" status="PASS"/>
                            </class>
                        </test>
                    </suite>
                </testng-results>
                """).encode('utf-8')))


times = [
    (
        datetime.datetime(2017, 5, 8, 14, 14, 59, 0), '2017-05-08T14:14:59Z',
        datetime.datetime(2017, 5, 8, 14, 15, 17, 34000), '2017-05-08T14:15:17Z', 18034, 18034),
    (
        datetime.datetime(2017, 5, 8, 14, 15, 59, 0), '2017-05-08T14:15:59Z',
        datetime.datetime(2017, 5, 8, 14, 16, 17, 34000), '2017-05-08T14:16:17Z', 18034, 78034),
    (
        datetime.datetime(2017, 5, 8, 14, 16, 59, 0), '2017-05-08T14:16:59Z',
        datetime.datetime(2017, 5, 8, 14, 17, 17, 34000), '2017-05-08T14:17:17Z', 18034, 138034),
]


def no_exception(time_index, verdict):
    return dedent(
        """\
    <?xml version="1.0" encoding="utf-8"?>
    <testng-results version="1.0">
        <reporter-output/>
        <suite duration-ms="{duration}" finished-at="{finished_at}" name="Name of Suite" started-at="{started_at}">
            <groups/>
            <test duration-ms="{duration}" finished-at="{finished_at}" name="Name of Suite" started-at="{started_at}">
                <class name="a.b">
                    <test-method duration-ms="{duration}" finished-at="{finished_at}" name="tc1" signature="a.b.tc1" started-at="{started_at}" status="{verdict}"/>
                </class>
            </test>
        </suite>
    </testng-results>
    """).format(
            started_at=times[time_index][1],
            finished_at=times[time_index][3],
            duration=times[time_index][4],
            verdict=verdict).encode('utf-8')


def with_exception(time_index, verdict, stacktrace):
    return dedent(
        """\
    <?xml version="1.0" encoding="utf-8"?>
    <testng-results version="1.0">
        <reporter-output/>
        <suite duration-ms="{duration}" finished-at="{finished_at}" name="Name of Suite" started-at="{started_at}">
            <groups/>
            <test duration-ms="{duration}" finished-at="{finished_at}" name="Name of Suite" started-at="{started_at}">
                <class name="a.b">
                    <test-method duration-ms="{duration}" finished-at="{finished_at}" name="tc1" signature="a.b.tc1" started-at="{started_at}" status="{verdict}">
                        <exception class="AssertionError">
                            <message>
    <![CDATA[assert failed.]]>                            \


                            </message>
                            <full-stacktrace>
    <![CDATA[AssertionError: assert failed.
    {stacktrace}]]>                            \


                            </full-stacktrace>
                        </exception>
                        <reporter-output/>
                    </test-method>
                </class>
            </test>
        </suite>
    </testng-results>
    """).format(
            started_at=times[time_index][1],
            finished_at=times[time_index][3],
            duration=times[time_index][4],
            verdict=verdict,
            stacktrace=stacktrace).encode('utf-8')


def results(tcs, suite_name='Name of Suite', run_verdict=Verdict.PASSED):
    message = None
    if run_verdict != Verdict.PASSED:
        message = dedent(
            """\
            A
            multiline
            error
            message
            """)

    run_result = TestRunResult(suite_name, tcs[0].start_time)
    run_result.set_finished(tcs[-1].end_time, run_verdict, message)

    return ResultsCollection(tcs, run_result)


def tc(verdict, time_index, exception=None, stacktrace=''):
    tc = TestCaseResult('tc1', 'a.b.tc1', times[time_index][0])
    tc.set_finished(times[time_index][2], verdict, exception, stacktrace)
    return tc
