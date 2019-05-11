"""
Tests the classes in the cli module.

Note: uses relative imports and hence the parent module need to be loaded.
"""
import sys
import unittest

from ..loganalyzercli import LogAnalyzerCLI


class TestCmdLineParsingDefaults(unittest.TestCase):

    def setUp(self):
        super().setUp()
        argv = 'zloganalyzer -'.split()
        self.args = LogAnalyzerCLI().parse_commandline_args(argv)

    def test_reads_infile_from_stdin_by_default(self):
        self.assertEqual(sys.stdin, self.args.infile)

    def test_writes_report_to_stdout_by_default(self):
        self.assertEqual(sys.stdout, self.args.outfile)

    def test_writes_summary_to_stdout_by_default(self):
        self.assertEqual(sys.stdout, self.args.summaryfile)

    def test_does_not_write_log_by_default(self):
        self.assertIsNone(self.args.logfile_path)


class TestCmdLineParsingDashAsStdinStdout(unittest.TestCase):

    def setUp(self):
        super().setUp()
        argv = 'zloganalyzer --in - --out - --summary - --logfile - -'.split()
        self.args = LogAnalyzerCLI().parse_commandline_args(argv)

    def test_dash_works_as_stdin_for_config(self):
        self.assertEqual(sys.stdin, self.args.configfile)

    def test_dash_works_as_stdin_for_in(self):
        self.assertEqual(sys.stdin, self.args.infile)

    def test_dash_works_as_stdout_for_out(self):
        self.assertEqual(sys.stdout, self.args.outfile)

    def test_dash_works_as_stdout_for_summary(self):
        self.assertEqual(sys.stdout, self.args.summaryfile)
