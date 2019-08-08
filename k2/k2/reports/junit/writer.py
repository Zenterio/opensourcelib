import logging

from junit_xml import TestCase, TestSuite
from zaf.extensions.extension import get_logger_name

from k2.results.results import TestCaseResult
from k2.runner.testcase import Verdict

logger = logging.getLogger(get_logger_name('k2', 'junitreport'))
logger.addHandler(logging.NullHandler())

VERDICT_TO_JUNIT_STATUS_MAPPING = {
    Verdict.PASSED: 'SUCCESSFUL',
    Verdict.FAILED: 'FAILED',
    Verdict.ERROR: 'FAILED',
    Verdict.PENDING: 'FAILED',
    Verdict.SKIPPED: 'SUCCESSFUL',
    Verdict.IGNORED: 'SUCCESSFUL',
}


def write_junit_report(test_result, report_file):
    """
    Generate a Junit XML Report from the test results.

    :param test_result: k2.results.results.ResultsCollection
    :param report_file: where to write the report
    """
    with open(report_file, 'w') as f:
        f.write(generate_junit_report(test_result))


def generate_junit_report(test_result):
    """
    Generate a Junit XML Report from the test results as a junit_xml.TestSuite.

    :param test_result: k2.results.results.ResultsCollection
    :return: string with the XML content
    """
    suite_name = test_result.run_result.name
    suite_start = test_result.run_result.start_time

    # Mapping the run result to a test case result to be able to include it in the report
    # The junit_xml package calculates the suite duration from the test case durations so we
    # need to make the suite duration 0 in the extra test case to not get strange results.
    test_results = list(test_result.test_results)
    if test_result.run_result.verdict != Verdict.PASSED and test_result.run_result.message:
        suite_result = TestCaseResult(suite_name, suite_name, suite_start)
        suite_result.set_finished(
            suite_start, test_result.run_result.verdict, test_result.run_result.message, '')
        test_results.append(suite_result)

    junit_suite = TestSuite(
        name=suite_name,
        test_cases=[map_to_junit_test_case(tc) for tc in test_results],
        timestamp=suite_start.isoformat(timespec='seconds'),
    )
    return TestSuite.to_xml_string([junit_suite], prettyprint=True, encoding='utf-8')


def map_to_junit_test_case(test_case):
    junit_tc = TestCase(
        name=_get_name_with_params(test_case),
        classname=test_case.qualified_name.rsplit('.', maxsplit=1)[0],
        elapsed_sec=test_case.duration.total_seconds(),
        timestamp=test_case.start_time.isoformat(timespec='seconds'),
        status=VERDICT_TO_JUNIT_STATUS_MAPPING[test_case.verdict],
    )

    if test_case.verdict == Verdict.FAILED:
        junit_tc.add_failure_info(message=test_case.exception, output=test_case.stacktrace)
    elif test_case.verdict == Verdict.ERROR:
        junit_tc.add_error_info(message=test_case.exception, output=test_case.stacktrace)
    elif test_case.verdict in [Verdict.SKIPPED, Verdict.IGNORED]:
        junit_tc.add_skipped_info(message=test_case.exception, output=test_case.stacktrace)

    return junit_tc


def _get_name_with_params(test_case):
    return test_case.name + '[' + ', '.join(
        test_case.params) + ']' if test_case.params else test_case.name
