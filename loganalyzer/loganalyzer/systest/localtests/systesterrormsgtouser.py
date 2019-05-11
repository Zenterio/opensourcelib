"""Tests the error messages given to user for different types of basic errors, and in different modes."""

import logging
from unittest.mock import patch

from loganalyzer import loganalyzercli
from loganalyzer.configreaders import ConfigError
from loganalyzer.datasources import DataSourceError
from loganalyzer.loganalyzercli import LogAnalyzerCLI
from loganalyzer.reporters import ReportingError
from loganalyzer.systest.utils import assert_installed

from ..systest import SysTest


class TestErrorInApplication(SysTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert_installed('zloganalyzer')

    def setUp(self):
        super().setUp()
        self.argv = [
            'zloganalyzer', '--quiet', '--in',
            self.data_file('minimal.in'),
            self.config_file('minimal.yaml')
        ]
        self.handler = None

    def tearDown(self):
        self._remove_loghandler()
        super().tearDown()

    def _set_loghandler(self, level, filename):
        filepath = self.build_file(filename)
        handler = logging.FileHandler(filepath, mode='w', delay=True)
        handler.setLevel(level)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        self.handler = handler

    def _remove_loghandler(self):
        logging.getLogger().removeHandler(self.handler)

    @patch(
        loganalyzercli.__name__ + '.StreamDataSource.get_data',
        side_effect=DataSourceError('Induced data error'))
    def test_datasrc_error_running_app_as_in_std_mode(self, DataSourceMock):
        out = 'datasrc_error_std_mode.txt'
        app = LogAnalyzerCLI(False, None, self.argv)
        self._set_loghandler(logging.CRITICAL, out)
        with app:
            app.run()
        self.filter_out_path_dependencies(self.build_file(out))
        self.assertEqual(4, app.exit_code)
        self.baseline_check(out)

    @patch(
        loganalyzercli.__name__ + '.StreamDataSource.get_data',
        side_effect=DataSourceError('Induced data error'))
    def test_datasrc_error_running_app_as_in_verbose_mode(self, DataSourceMock):
        out = 'datasrc_error_verbose_mode.txt'
        app = LogAnalyzerCLI(True, None, self.argv)
        self._set_loghandler(logging.WARNING, out)
        with app:
            app.run()
        self.filter_out_path_dependencies(self.build_file(out))
        self.assertEqual(4, app.exit_code)
        self.baseline_check(out)

    @patch(
        loganalyzercli.__name__ + '.YAMLConfigReader.get_config',
        side_effect=ConfigError('Induced rule configuration error'))
    def test_rule_config_error_running_app_as_in_std_mode(self, ConfigMock):
        out = 'rule_config_error_std_mode.txt'
        app = LogAnalyzerCLI(False, None, self.argv)
        self._set_loghandler(logging.CRITICAL, out)
        with app:
            app.run()
        self.filter_out_path_dependencies(self.build_file(out))
        self.assertEqual(4, app.exit_code)
        self.baseline_check(out)

    @patch(
        loganalyzercli.__name__ + '.YAMLConfigReader.get_config',
        side_effect=ConfigError('Induced rule configuration error'))
    def test_rule_config_error_running_app_as_in_verbose_mode(self, ConfigMock):
        out = 'rule_config_error_verbose_mode.txt'
        app = LogAnalyzerCLI(True, None, self.argv)
        self._set_loghandler(logging.WARNING, out)
        with app:
            app.run()
        self.filter_out_path_dependencies(self.build_file(out))
        self.assertEqual(4, app.exit_code)
        self.baseline_check(out)

    @patch(
        loganalyzercli.__name__ + '.TextReporter.write_report',
        side_effect=ReportingError('Induced reporting error'))
    def test_reporter_error_running_app_as_in_std_mode(self, ReporterMock):
        out = 'reporter_error_std_mode.txt'
        app = LogAnalyzerCLI(False, None, self.argv)
        self._set_loghandler(logging.CRITICAL, out)
        with app:
            app.run()
        self.filter_out_path_dependencies(self.build_file(out))
        self.assertEqual(4, app.exit_code)
        self.baseline_check(out)

    @patch(
        loganalyzercli.__name__ + '.TextReporter.write_report',
        side_effect=ReportingError('Induced reporting error'))
    def test_reporter_error_running_app_as_in_verbose_mode(self, ReporterMock):
        out = 'reporter_error_verbose_mode.txt'
        app = LogAnalyzerCLI(False, None, self.argv)
        self._set_loghandler(logging.WARNING, out)
        with app:
            app.run()
        self.filter_out_path_dependencies(self.build_file(out))
        self.assertEqual(4, app.exit_code)
        self.baseline_check(out)
