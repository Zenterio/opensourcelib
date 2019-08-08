import unittest
from textwrap import dedent

from k2_jenkins.jenkins import BuildInfo


class TestBuildInfo(unittest.TestCase):

    def setUp(self):
        self._build_info = BuildInfo('jenkins_url', 'job', 3, 'SUCCESS', console_log, artifacts)

    def test_assert_result_when_equal(self):
        self._build_info.assert_result('SUCCESS')

    def test_assert_result_when_not_equal(self):
        with self.assertRaises(AssertionError):
            self._build_info.assert_result('FAILURE')

    def test_assert_not_result_when_equal(self):
        with self.assertRaises(AssertionError):
            self._build_info.assert_not_result('SUCCESS')

    def test_assert_not_result_when_not_equal(self):
        self._build_info.assert_not_result('FAILURE')

    def test_assert_in_console_log_when_in(self):
        self._build_info.assert_in_console_log('in')

    def test_assert_in_console_log_when_not_in(self):
        with self.assertRaises(AssertionError):
            self._build_info.assert_in_console_log('not in')

    def test_assert_not_in_console_log_when_in(self):
        with self.assertRaises(AssertionError):
            self._build_info.assert_not_in_console_log('in')

    def test_assert_not_in_console_log_when_not_in(self):
        self._build_info.assert_not_in_console_log('not in')

    def test_assert_in_artifacts_when_in(self):
        self._build_info.assert_in_artifacts('path/to/artifact1')

    def test_assert_in_artifacts_when_not_in(self):
        with self.assertRaises(AssertionError):
            self._build_info.assert_in_artifacts('not/an/artifact')

    def test_assert_not_in_artifacts_when_in(self):
        with self.assertRaises(AssertionError):
            self._build_info.assert_not_in_artifacts('another/path/to/artifact2')

    def test_assert_not_in_artifacts_when_not_in(self):
        self._build_info.assert_not_in_artifacts('not/an/artifact')


artifacts = [
    'path/to/artifact1',
    'another/path/to/artifact2',
]

console_log = dedent("""\
    console
    log
    in
    """)
