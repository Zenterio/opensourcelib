import os
import sys
from collections import defaultdict
from textwrap import dedent, indent

from k2.runner.testcase import Verdict


def write_report(test_result, outputs, template, show_owner):
    """
    Generate a Human Readable Report from the test results.

    :param test_result: k2.results.results.ResultsCollection
    :param report_file: where to write the report
    :param template: Output template, dictates how much information is included
    """
    report = generate_report(test_result, template, show_owner)

    for output in outputs:
        if output == '-':
            sys.stdout.write(report)
        else:
            dir = os.path.dirname(output)
            if dir != '' and not os.path.exists(dir):
                os.makedirs(dir)
            with open(output, 'w') as out:
                out.write(report)


def generate_report(test_result, template, show_owner=False):
    """
    Generate a Human Readable Report from the test results.

    :param test_result: list of k2.results.results.TestCaseResult
    :param template: Output template, dictates how much information is included
    :return: Test report
    """

    testcases = dedent(
        """\
                Results ({verdict}): {suite_name}
                -------
                """)
    failures = dedent(
        """
               Failures/Errors:
               ----------------
               """)
    summary = dedent(
        """
              Summary: {suite_name}
              --------
              Passed:  {passed}
              Failed:  {failed}
              Error:   {error}
              Pending: {pending}
              Skipped: {skipped}
              Ignored: {ignored}
              Total:   {total}
              Execution time: {total_duration}
              """)
    verdict_counts = defaultdict(int)
    max_name_length = get_max_testname_length(test_result.test_results)

    testcases = testcases.format(
        suite_name=test_result.run_result.name, verdict=test_result.run_result.verdict.name)
    total_duration = (test_result.run_result.end_time - test_result.run_result.start_time)
    if test_result.run_result.verdict in [Verdict.FAILED, Verdict.ERROR
                                          ] and test_result.run_result.message:
        failures += '{name}\n{message}\n\n'.format(
            name=test_result.run_result.name, message=test_result.run_result.message)

    for test_case in test_result.test_results:
        name = test_case.name + '[' + ', '.join(
            test_case.params) + ']' if test_case.params else test_case.name
        verdict = test_case.verdict
        verdict_counts[verdict] += 1
        duration = test_case.duration
        testcases += '{name:<{max_name_length}} {verdict:<7} {duration}\n' \
            .format(name=name, max_name_length=max_name_length, verdict=verdict.name, duration=duration)
        if verdict in [Verdict.FAILED, Verdict.ERROR]:
            owner = test_case.owner if test_case.owner is not None else test_result.run_result.owner
            if show_owner and owner is not None:
                failures += '{name} (Test case owner: {owner})\n'.format(name=name, owner=owner)
            else:
                failures += '{name}\n'.format(name=name)
            if test_case.stacktrace:
                msg = '{stacktrace}\n'.format(stacktrace=test_case.stacktrace)
                failures += indent(msg, '  ')
            elif test_case.exception:
                msg = '{exception}\n'.format(exception=test_case.exception)
                failures += indent(msg, '  ')
            failures += '\n'
    summary = summary.format(
        passed=verdict_counts[Verdict.PASSED],
        failed=verdict_counts[Verdict.FAILED],
        error=verdict_counts[Verdict.ERROR],
        pending=verdict_counts[Verdict.PENDING],
        skipped=verdict_counts[Verdict.SKIPPED],
        ignored=verdict_counts[Verdict.IGNORED],
        total=(
            verdict_counts[Verdict.PASSED] + verdict_counts[Verdict.FAILED] +
            verdict_counts[Verdict.ERROR] + verdict_counts[Verdict.PENDING] +
            verdict_counts[Verdict.SKIPPED] + verdict_counts[Verdict.IGNORED]),
        total_duration=total_duration,
        suite_name=test_result.run_result.name)

    result = ''
    if template in ['full']:
        result += testcases

    if template in ['full', 'brief']:
        result += failures

    result += summary

    return result


def get_max_testname_length(test_results):
    return max([0] + list(map(lambda tc: len(tc.name), test_results)))
