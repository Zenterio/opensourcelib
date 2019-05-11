"""Tests that errors in rule configuration is reported accurately to the user."""
from loganalyzer.systest.utils import assert_installed

from ..systest import SysTest


class TestConfig(SysTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert_installed('zloganalyzer')

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_invalid_yaml(self):
        stderr = 'invalid_yaml.txt'
        self.fail_proc(
            [
                'zloganalyzer', '--in',
                self.data_file('minimal.in'),
                self.config_file('invalid_yaml.yaml')
            ],
            exit_code=4,
            outfile=stderr)
        self.baseline_check(stderr)

    def test_invalid_markers(self):
        stderr = 'invalid_markers.txt'
        self.fail_proc(
            [
                'zloganalyzer', '--in',
                self.data_file('minimal.in'),
                self.config_file('invalid_marker.yaml')
            ],
            exit_code=4,
            outfile=stderr)
        self.baseline_check(stderr)

    def test_missing_definition(self):
        stderr = 'missing_definition.txt'
        self.fail_proc(
            [
                'zloganalyzer', '--in',
                self.data_file('minimal.in'),
                self.config_file('missing_definitions.yaml')
            ],
            exit_code=4,
            outfile=stderr)
        self.baseline_check(stderr)

    def test_invalid_items_and_markers(self):
        stderr = 'invalid_items_and_markers.txt'
        self.fail_proc(
            [
                'zloganalyzer', '--in',
                self.data_file('minimal.in'),
                self.config_file('invalid_items_and_markers.yaml')
            ],
            exit_code=4,
            outfile=stderr)
        self.baseline_check(stderr)

    def test_invalid_watchers(self):
        stderr = 'invalid_watchers.txt'
        self.fail_proc(
            [
                'zloganalyzer', '--in',
                self.data_file('minimal.in'),
                self.config_file('invalid_watchers.yaml')
            ],
            exit_code=4,
            outfile=stderr)
        self.baseline_check(stderr)

    def test_config_checker_missing_samples(self):
        stderr = 'syntax_checker_samples_missing.txt'
        self.fail_proc(
            [
                'zloganalyzer', '--in',
                self.data_file('minimal.in'), '--config-check-only',
                self.config_file('minimal.yaml')
            ],
            exit_code=4,
            outfile=stderr,
            cwd=self.BUILD_DIR)
        self.baseline_check(stderr)

    def test_config_checker_complete_samples(self):
        stdout = 'syntax_checker_complete_samples.txt'
        self.exec_proc(
            [
                'zloganalyzer', '--in',
                self.data_file('minimal.in'), '--config-check-only',
                self.config_file('example.yaml')
            ],
            outfile=stdout,
            cwd=self.BUILD_DIR)
        self.baseline_check(stdout)

    def test_config_checker_duplicate_ids(self):
        stderr = 'config_checker_duplicate_ids.txt'
        self.fail_proc(
            [
                'zloganalyzer', '--in',
                self.data_file('minimal.in'), '--config-check-only',
                self.config_file('duplicate_id.yaml')
            ],
            exit_code=4,
            outfile=stderr,
            cwd=self.BUILD_DIR)
        self.baseline_check(stderr)
