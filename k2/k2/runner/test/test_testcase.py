import unittest
from unittest.mock import MagicMock

from k2.finder.testfinder import TestCaseParam

from ..exceptions import DisabledException, SkipException
from ..testcase import RunnerTestCase, Verdict


class TestTestCase(unittest.TestCase):

    @staticmethod
    def do_nothing():
        pass

    def test_case_result_is_initially_pending(self):
        assert RunnerTestCase(TestTestCase.do_nothing).verdict == Verdict.PENDING

    def test_case_exception_is_initially_none(self):
        assert RunnerTestCase(TestTestCase.do_nothing).exception is None

    def test_setting_exception_to_assertion_error_yields_failed_result(self):
        tc = RunnerTestCase(TestTestCase.do_nothing)
        my_assertion_error = AssertionError('computer sais no')
        tc.update_verdict(my_assertion_error, 'stacktrace')
        assert tc.exception == my_assertion_error
        assert tc.verdict == Verdict.FAILED

    def test_setting_exception_to_skip_exception_yields_skipped_result(self):
        tc = RunnerTestCase(TestTestCase.do_nothing)
        my_assertion_error = SkipException('computer sais no')
        tc.update_verdict(my_assertion_error, 'stacktrace')
        assert tc.exception == my_assertion_error
        assert tc.verdict == Verdict.SKIPPED

    def test_setting_exception_to_disabled_exception_yields_ignored_result(self):
        tc = RunnerTestCase(TestTestCase.do_nothing)
        my_assertion_error = DisabledException('computer sais no')
        tc.update_verdict(my_assertion_error, 'stacktrace')
        assert tc.exception == my_assertion_error
        assert tc.verdict == Verdict.IGNORED

    def test_setting_exception_to_exception_yields_error_result(self):
        tc = RunnerTestCase(TestTestCase.do_nothing)
        my_assertion_error = Exception('computer sais no')
        tc.update_verdict(my_assertion_error, 'stacktrace')
        assert tc.exception == my_assertion_error
        assert tc.verdict == Verdict.ERROR

    def test_setting_exception_to_none_yields_passing_result(self):
        tc = RunnerTestCase(TestTestCase.do_nothing)
        tc.update_verdict(None)
        assert tc.exception is None
        assert tc.verdict == Verdict.PASSED

    def test_calling_run_method_calls_the_run_function(self):
        m = MagicMock()
        tc = RunnerTestCase(m, name='run')
        tc.run()
        m.assert_called_once_with()

    def test_combines_test_run_verdicts(self):
        assert Verdict.PASSED.combine(Verdict.PASSED) == Verdict.PASSED
        assert Verdict.PASSED.combine(Verdict.FAILED) == Verdict.FAILED
        assert Verdict.FAILED.combine(Verdict.FAILED) == Verdict.FAILED
        assert Verdict.PASSED.combine(Verdict.PENDING) == Verdict.ERROR
        assert Verdict.FAILED.combine(Verdict.ERROR) == Verdict.ERROR
        assert Verdict.ERROR.combine(Verdict.ERROR) == Verdict.ERROR

    def test_full_name_includes_params(self):
        params = [TestCaseParam('k1', 'v1', str, False), TestCaseParam('k2', 'v2', str, False)]
        tc = RunnerTestCase(TestTestCase.do_nothing, params=params)
        assert tc.full_name == 'do_nothing[k1=v1,k2=v2]'
