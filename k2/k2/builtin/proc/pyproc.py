"""
Provides component for dealing with python subprocesses.

Support for running python subprocess with coverage enabled.
"""
import logging
import os
import subprocess
import sys

from zaf.application import AFTER_COMMAND, APPLICATION_ENDPOINT
from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND

from . import COVERAGE_CONFIG_FILE, COVERAGE_ENABLED, COVERAGE_REPORT, COVERAGE_XML_REPORT

logger = logging.getLogger(get_logger_name('k2', 'pyproc'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    'pyproc',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(COVERAGE_CONFIG_FILE, required=False),
        ConfigOption(COVERAGE_ENABLED, required=False),
        ConfigOption(COVERAGE_REPORT, required=False),
        ConfigOption(COVERAGE_XML_REPORT, required=False),
    ])
class PyProcExtension(AbstractExtension):

    def __init__(self, config, instances):
        coverage_enabled = config.get(COVERAGE_ENABLED, False)
        self.coverage_enabled = coverage_enabled

        if coverage_enabled:
            coverage_config_file = os.path.abspath(config.get(COVERAGE_CONFIG_FILE))
            coverage_report = config.get(COVERAGE_REPORT)
            self.coverage_report = None if coverage_report is None else os.path.abspath(
                coverage_report)
            coverage_xml_report = config.get(COVERAGE_XML_REPORT)
            self.coverage_xml_report = None if coverage_xml_report is None else os.path.abspath(
                coverage_xml_report)

            config_file_arg = ''
            if coverage_config_file:
                config_file_arg = '--rcfile {file}'.format(file=coverage_config_file)
            self.config_file_arg = config_file_arg

        @component(provided_by_extension='pyproc', scope='session')
        @requires(process_runner='ProcessRunner')
        class PyProc(object):
            """Make it easy to execute python based programs with an entry point."""

            def __init__(self, name, process_runner):
                """
                Create a new PyProc.

                :param name: Name of the command/entry point to execute.
                :param process_runner: The process runner.
                """
                self.process_runner = process_runner
                self.name = name

            def __call__(
                    self,
                    arguments,
                    expected_exit_code=0,
                    wait=True,
                    timeout=None,
                    env=None,
                    cwd=None,
                    command_prefix=''):
                """
                Invoke the command/entry point.

                :raises AssertionError: if the expected exit code is not fullfilled.
                :param arguments: The arguments to pass to the command as a string.
                :param expected_exit_code: The expected exit code, defaults to 0.
                :param wait: Wait for command to finish, defaults to True.
                :param timeout: Wait for command to finish, defaults to True.
                :param env: Dict with additional environment variables
                :param cwd: Change current working directory to this
                :return: Process object
                """

                if coverage_enabled:
                    coverage = 'COVERAGE_FILE={coverage_file} coverage run {config_file_arg} --parallel-mode'.format(
                        coverage_file=coverage_report, config_file_arg=config_file_arg)
                else:
                    coverage = ''

                entry_point = subprocess.check_output(
                    ['which', self.name], universal_newlines=True).strip()

                command = '{prefix} {coverage} {entry_point} {arguments}'.format(
                    prefix=command_prefix,
                    coverage=coverage,
                    entry_point=entry_point,
                    arguments=arguments)

                logger.debug('Using env: {env}'.format(env=repr(env)))
                logger.info(
                    'Running command{cwd_message}: {command}'.format(
                        command=command, cwd_message=' in {cwd}'.format(cwd=cwd) if cwd else ''))
                return self.process_runner(
                    command,
                    expected_exit_code=expected_exit_code,
                    wait=wait,
                    timeout=timeout,
                    env=env,
                    cwd=cwd)

    @callback_dispatcher([AFTER_COMMAND], [APPLICATION_ENDPOINT])
    def after_command(self, message):
        if self.coverage_enabled:
            if os.path.exists(self.coverage_report):
                os.remove(self.coverage_report)

            combine_command = 'COVERAGE_FILE={report} coverage combine {report}*'.format(
                report=self.coverage_report)
            subprocess.check_call(combine_command, shell=True, universal_newlines=True)

            report_command = 'COVERAGE_FILE={report} coverage report -m {config_file_arg}'.format(
                report=self.coverage_report, config_file_arg=self.config_file_arg)
            subprocess.check_call(report_command, stdout=sys.stdout, stderr=sys.stderr, shell=True)

            if self.coverage_xml_report:
                xml_command = 'COVERAGE_FILE={report} coverage xml -o {xml_report} {config_file_arg}'.format(
                    report=self.coverage_report,
                    xml_report=self.coverage_xml_report,
                    config_file_arg=self.config_file_arg)
                subprocess.check_call(xml_command, stdout=sys.stdout, stderr=sys.stderr, shell=True)
