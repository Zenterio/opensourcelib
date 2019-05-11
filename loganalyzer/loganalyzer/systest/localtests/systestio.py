"""Tests the cli help output."""
from loganalyzer.configreaders import EnvVarConfigReader
from loganalyzer.systest.utils import assert_installed

from ..systest import SysTest


class TestInputOutputWithValidFiles(SysTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert_installed('zloganalyzer')

    def setUp(self):
        super().setUp()
        self.data_in = self.data_file('minimal.in')
        self.latin_1_in = self.data_file('latin_1.in')
        self.utf8_in = self.data_file('utf8.in')
        self.config_file = self.config_file('minimal.yaml')

    def set_config(self, name):
        self.report = '{name}.report.txt'.format(name=name)
        self.summary = '{name}.summary.txt'.format(name=name)
        self.report_and_summary = '{name}.report.summary.txt'.format(name=name)
        self.gen_report = self.build_file(self.report)
        self.gen_summary = self.build_file(self.summary)

    def tearDown(self):
        super().tearDown()

    def test_in_can_read_automatically_from_utf_8_file(self):
        self.set_config('utf8')
        cmd = 'zloganalyzer -v --in {infile} {config}'.format(
            infile=self.utf8_in, config=self.config_file)
        self.exec_shell(cmd, self.report_and_summary, cwd=self.BUILD_DIR)
        self.baseline_check(self.report_and_summary)

    def test_in_can_read_automatically_from_latin_1_file(self):
        self.set_config('latin_1')
        cmd = 'zloganalyzer -v --in {infile} {config}'.format(
            infile=self.latin_1_in, config=self.config_file)
        self.exec_shell(cmd, self.report_and_summary, cwd=self.BUILD_DIR)
        self.baseline_check(self.report_and_summary)

    def test_in_can_read_from_file_using_forced_encoding_from_env(self):
        self.set_config('env_encoding')
        cmd = '{encoding}=latin_1 zloganalyzer -v --in {infile} {config}'.format(
            infile=self.latin_1_in, config=self.config_file, encoding=EnvVarConfigReader.ENCODING)
        self.exec_shell(cmd, self.report_and_summary, cwd=self.BUILD_DIR)
        self.baseline_check(self.report_and_summary)

    def test_in_can_read_from_file_using_forced_encoding_from_cmdline(self):
        self.set_config('cmdline_encoding')
        cmd = 'zloganalyzer -v --set-encoding latin_1 --in {infile} {config}'.format(
            infile=self.latin_1_in, config=self.config_file)
        self.exec_shell(cmd, self.report_and_summary, cwd=self.BUILD_DIR)
        self.baseline_check(self.report_and_summary)

    def test_report_can_write_to_file(self):
        self.set_config('minimal')
        cmd = 'zloganalyzer -v --in {infile} --out {out} {config}'.format(
            infile=self.data_in, out=self.gen_report, config=self.config_file)
        self.exec_shell(cmd, self.summary, cwd=self.BUILD_DIR)
        self.baseline_check(self.report)

    def test_summary_can_write_to_file(self):
        self.set_config('minimal')
        cmd = ('zloganalyzer -v --in {infile}'
               ' --summary {summary} {config}').format(
                   infile=self.data_in, summary=self.gen_summary, config=self.config_file)
        self.exec_shell(cmd, cwd=self.BUILD_DIR)
        self.baseline_check(self.summary)

    def test_check_encoding_autodetect(self):
        out = 'check_encoding_autodetect.txt'
        cmd = (
            'zloganalyzer -v --in {infile} --encoding-check-only {config}'.format(
                infile=self.latin_1_in, config=self.config_file))
        self.exec_shell(cmd, out, cwd=self.BUILD_DIR)
        self.baseline_check(out)

    def test_check_encoding_forced_encoding(self):
        out = 'check_encoding_forced.txt'
        cmd = (
            'zloganalyzer -v --in {infile} --set-encoding utf8 --encoding-check-only {config}'.
            format(infile=self.utf8_in, config=self.config_file))
        self.exec_shell(cmd, out, cwd=self.BUILD_DIR)
        self.baseline_check(out)


class TestInputOutputWithInvalidFiles(SysTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert_installed('zloganalyzer')

    def setUp(self):
        super().setUp()
        self.config_file = self.config_file('minimal.yaml')
        self.data_in = self.data_file('minimal.in')

    def tearDown(self):
        super().tearDown()

    def test_missing_infile_exit_code_2(self):
        out = 'invalid_infile.txt'
        cmd = 'zloganalyzer  -v --in {infile} {config}'.format(
            infile='invalid', config=self.config_file)
        self.fail_shell(cmd, 2, out, cwd=self.BUILD_DIR)
        self.baseline_check(out)

    def test_write_protected_outfile_exit_code_2(self):
        out = 'write_protected_outfile.txt'
        cmd = 'zloganalyzer  -v --out {out} {config}'.format(
            out='/root/loganalyzer.systest.txt', config=self.config_file)
        self.fail_shell(cmd, 2, out, cwd=self.BUILD_DIR)
        self.baseline_check(out)

    def test_write_protected_summaryfile_exit_code_2(self):
        out = 'write_protected_summaryfile.txt'
        cmd = 'zloganalyzer  -v --in {infile} --summary {summary} {config}'.format(
            summary='/root/loganalyzer.systest.txt', config=self.config_file, infile=self.data_in)
        self.fail_shell(cmd, 2, out, cwd=self.BUILD_DIR)
        self.baseline_check(out)

    def test_outfile_in_missing_directory_exit_code_2(self):
        out = 'missing_directory_outfile.txt'
        outfile = self.build_file('invalid_dir/report.txt')
        cmd = 'zloganalyzer  -v --out {out} {config}'.format(out=outfile, config=self.config_file)
        self.fail_shell(cmd, 2, out, cwd=self.BUILD_DIR)
        self.baseline_check(out)

    def test_summary_in_missing_directory_exit_code_2(self):
        out = 'missing_directory_summary.txt'
        summaryfile = self.build_file('invalid_dir/summary.txt')
        cmd = 'zloganalyzer  -v --summary {summary} {config}'.format(
            summary=summaryfile, config=self.config_file)
        self.fail_shell(cmd, 2, out, cwd=self.BUILD_DIR)
        self.baseline_check(out)

    def test_missing_config_exit_code_2(self):
        out = 'invalid_config.txt'
        cmd = 'zloganalyzer  -v {config}'.format(config='invalid')
        self.fail_shell(cmd, 2, out, cwd=self.BUILD_DIR)
        self.baseline_check(out)

    def test_forcing_wrong_encoding_ignores_errors(self):
        out = 'forced_wrong_encoding.txt'
        infile = self.data_file('latin_1.in')
        cmd = 'zloganalyzer --set-encoding utf8 --in {infile} {config}'.format(
            infile=infile, config=self.config_file)
        self.exec_shell(cmd, out, cwd=self.BUILD_DIR)
        self.baseline_check(out)
