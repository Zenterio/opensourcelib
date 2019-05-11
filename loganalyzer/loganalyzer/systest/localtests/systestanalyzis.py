"""Tests basic analysis by parsing a minimal input using a minimal rule configuration."""
from loganalyzer.systest.utils import assert_installed

from ..systest import SysTest


class TestAnalyzis(SysTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert_installed('zloganalyzer')

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_minimal(self):
        report = 'minimal.report.txt'
        summary = 'minimal.summary.txt'
        self.exec_proc(
            [
                'zloganalyzer', '-v', '--in',
                self.data_file('minimal.in'), '--out',
                self.build_file(report),
                self.config_file('minimal.yaml')
            ], self.build_file(summary))
        self.baseline_check(summary)
        self.baseline_check(report)
