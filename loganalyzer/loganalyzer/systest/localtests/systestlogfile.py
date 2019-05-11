"""Tests the log file handling."""
from tempfile import NamedTemporaryFile

from loganalyzer.systest.utils import assert_installed

from ..systest import SysTest


class TestLogHandling(SysTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert_installed('zloganalyzer')

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_logfile_can_be_set_on_commandline(self):
        with NamedTemporaryFile(mode='w') as f:
            self.exec_proc(
                [
                    'zloganalyzer', '--verbose', '--in',
                    self.data_file('minimal.log'), '--logfile', f.name,
                    self.config_file('minimal.yaml')
                ])
            self.assertFileNotEmpty(f.name)

    def test_logfile_is_off_by_default(self):
        self.exec_proc(
            [
                'zloganalyzer', '--verbose', '--in',
                self.data_file('minimal.log'),
                self.config_file('minimal.yaml')
            ],
            cwd=self.BUILD_DIR)
