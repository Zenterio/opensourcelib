"""Tests the cli help output."""
from loganalyzer.systest.utils import assert_installed

from ..systest import SysTest


class TestHelp(SysTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert_installed('zloganalyzer')

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_h_prints_help_and_exits_with_code_0(self):
        self.exec_proc_and_baseline_check([
            'zloganalyzer',
            '-h',
        ], 'help.txt')

    def test_help_prints_help_and_exits_with_code_0(self):
        self.exec_proc_and_baseline_check([
            'zloganalyzer',
            '--help',
        ], 'help.txt')
