#!/usr/bin/env python3
# encoding: utf-8
"""
CLI application to run Log Analyzer.

@copyright:  2016 Zenterio AB. All rights reserved.
@license:    Apache 2.0 License
"""

import logging
import sys

from . import program_info
from .analyzer import AnalyzerFactory
from .appconfig import ConfigFactory, ConfigureLogger, log_config
from .application import LogAnalyzerApplication
from .configreaders import CmdLineConfigReader, ConfigError, EnvVarConfigReader, YAMLConfigReader
from .datasources import DataSourceError, StreamDataSource
from .reporters import ReportingError, TextReporter, WatchersReporter


class CLIError(Exception):
    """Generic exception to raise and log different fatal errors."""

    def __init__(self, msg):
        super().__init__(type(self))
        self.msg = 'E: {msg}'.format(msg=msg)

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


class LogAnalyzerCLI():

    logger = logging.getLogger('main')

    def __init__(self, debug=False, encoding=None, argv=None):
        self.debug = debug
        self.encoding = encoding
        self.argv = argv
        self.exit_code = 0

    def __enter__(self):
        args = self.parse_commandline_args(self.argv)
        logcfg = ConfigFactory().get_logconfig(args)
        self.configure_logger(logcfg)
        self.logger.info('Starting the cli-application')
        self.log_commandline_args(args)
        self.args = args
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info('Preparing to shutdown the cli-application')
        try:
            if exc_type == KeyboardInterrupt:
                print('')
                self.logger.warning('Aborted by user, keyboard interrupt detected.')
                self.exit_code = 0
            elif exc_type in [DataSourceError, ConfigError, ReportingError]:
                error_msg = str(exc_val)
                self.logger.critical(
                    program_info.name + ': Critical error, {err} \n - exiting application'.format(
                        err=error_msg))
                self.logger.error('Stack trace: ', exc_info=True)
                self.exit_code = 4
            elif exc_type is not None:
                self.logger.critical('An unexpected critical error occurred! Exiting Application')
                self.logger.error('Unhandled exception: ', exc_info=True)
                self.exit_code = 1
        finally:
            self.logger.info('Shutting down cli-application')
            logging.shutdown()

        return True  # Always suppress exceptions

    def run(self):
        if self.args.encoding_check:
            self.logger.info('Checking encoding of input file')
            print('Used encoding: {encoding}'.format(encoding=self.args.encoding))
            print('Detected encoding: {encoding}'.format(encoding=self.args.detected_encoding))
            print(
                'Detected confidence: {confidence}'.format(
                    confidence=self.args.detected_encoding_confidence))
        else:
            self.logger.info('Parsing rules configuration')
            config = YAMLConfigReader(self.args.configfile, self.args.config_check).get_config()
            if not self.args.config_check:
                self.logger.info('Assembling analysis-application')
                app = self._assemble_application(config)
                self.logger.info('Performing analysis')
                app.run()
                self.logger.info('Analysis done')

    def parse_commandline_args(self, argv=None):
        return CmdLineConfigReader(program_info, self.encoding, argv).get_config()

    def configure_logger(self, logcfg):
        ConfigureLogger().configure_logger(logcfg)

    def log_commandline_args(self, config):
        log_config('Commandline arguments:', config)

    def _assemble_application(self, config):
        analyzer = AnalyzerFactory().get_analyzer(config)
        datasource = StreamDataSource(self.args.infile)
        reporters = [TextReporter(self.args.summaryfile, self.args.outfile)]
        if self.args.watchers_file:
            reporters.append(
                WatchersReporter(self.args.watchers_file, self.args.watchers_separator))

        app = LogAnalyzerApplication(analyzer, datasource, *reporters)
        return app


def main():
    """Application entry point."""
    envcfg = EnvVarConfigReader().get_config()
    logging.raiseExceptions = envcfg.debug

    if envcfg.profile:
        exit_code = _profile_run(envcfg)
    else:
        exit_code = _run(envcfg.debug, envcfg.encoding)
    return exit_code


def _run(debug, encoding):
    with LogAnalyzerCLI(debug, encoding) as app:
        app.run()
    return app.exit_code


def _profile_run(envcfg):
    """Turn on profiling while running the application."""
    import cProfile
    import pstats
    profile_filename = 'zloganalyzer.profile.txt'
    stats_filename = 'zloganalyzer.stats.txt'
    cProfile.runctx(
        '_run(envcfg.debug, envcfg.encoding)', globals(), locals(), filename=profile_filename)
    with open(stats_filename, 'wt') as statsfile:
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.sort_stats('cumulative')
        stats.print_stats()
    return 0


if __name__ == '__main__':
    sys.exit(main())
