"""Tests that watchers file is created correctly."""
from loganalyzer.systest.utils import assert_installed

from ..systest import SysTest


class TestWatchers(SysTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert_installed('zloganalyzer')

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_watchers_file_with_separator(self):
        watchers = 'watchers.txt'

        self.exec_proc(
            [
                'zloganalyzer', '-v', '--in',
                self.data_file('minimal.in'), '--watchers-file',
                self.build_file(watchers), '--watchers-separator', '; ',
                self.config_file('minimal.yaml')
            ])
        self.baseline_check(watchers)
