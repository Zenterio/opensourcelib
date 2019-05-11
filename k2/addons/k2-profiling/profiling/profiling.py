"""
Profiles a K2 command invocation.

Collects a couple of metrics about the performance and behavior of the K2 execution.
It is not a replacement for proper profiling using python's built in
profiling tools, but is intended to be used to give a quick overview of K2 behavior.
"""

import logging
from time import perf_counter, process_time

from zaf.application import AFTER_COMMAND, APPLICATION_ENDPOINT, BEFORE_COMMAND
from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher
from zaf.utils.bashcompletion import NOT_BASH_COMPLETION, is_bash_completion

from k2 import PERF_COUNTER_K2_START, PROCESS_TIME_K2_START
from k2.utils.data import DataDefinition
from k2.utils.writers import CsvWriter, JsonWriter
from k2.utils.writers import SingleValueTextWriter as TextWriter

from . import PROFILING_CSV, PROFILING_CSV_PATH, PROFILING_DIR, PROFILING_JSON, \
    PROFILING_JSON_PATH, PROFILING_TEXT, PROFILING_TEXT_PATH

logger = logging.getLogger(get_logger_name('k2', 'profiling'))
logger.addHandler(logging.NullHandler())


class ProfilingDataDefinition(DataDefinition):

    def __init__(self):
        super().__init__(
            [
                'command', 'startup_time', 'command_execution_time', 'k2_execution_time',
                'startup_process_time', 'command_execution_process_time',
                'k2_execution_process_time'
            ], None)


class MeasurementDefinition(DataDefinition):

    def __init__(self):
        super().__init__(['k2_start', 'before_command', 'after_command', 'k2_exit'])


@FrameworkExtension(
    name='profiling',
    config_options=[
        ConfigOption(PROFILING_DIR, required=True),
        ConfigOption(PROFILING_CSV, required=False),
        ConfigOption(PROFILING_CSV_PATH, required=True),
        ConfigOption(PROFILING_JSON, required=False),
        ConfigOption(PROFILING_JSON_PATH, required=True),
        ConfigOption(PROFILING_TEXT, required=False),
        ConfigOption(PROFILING_TEXT_PATH, required=True),
        ConfigOption(NOT_BASH_COMPLETION, required=True),
    ],
    endpoints_and_messages={},
    activate_on=[(PROFILING_JSON, PROFILING_TEXT, PROFILING_CSV), NOT_BASH_COMPLETION])
class Profiling(AbstractExtension):
    """Profiles a K2 command invocation."""

    def __init__(self, config, instances):
        self._report_csv_enabled = config.get(PROFILING_CSV, False)
        self._report_csv_path = config.get(PROFILING_CSV_PATH, None)
        self._report_json_enabled = config.get(PROFILING_JSON, False)
        self._report_json_path = config.get(PROFILING_JSON_PATH, None)
        self._report_text_enabled = config.get(PROFILING_TEXT, False)
        self._report_text_path = config.get(PROFILING_TEXT_PATH, None)
        self._data = ProfilingDataDefinition()
        self._perfcount = MeasurementDefinition()
        self._perfcount.k2_start = PERF_COUNTER_K2_START
        self._process_time = MeasurementDefinition()
        self._process_time.k2_start = PROCESS_TIME_K2_START

        if is_bash_completion():
            self._enabled = False
        else:
            self._enabled = self._report_csv_enabled or self._report_json_enabled or \
                self._report_text_enabled   # or other future formats

        if self._enabled:
            import atexit
            atexit.register(self.on_exit)

    @callback_dispatcher([BEFORE_COMMAND], [APPLICATION_ENDPOINT])
    @requires(metric='CreateSingleValueMetric')
    def before_command(self, message, metric):
        self._perfcount.before_command = perf_counter()
        self._process_time.before_command = process_time()
        self._data.command = message.data
        self._data.startup_time = self._perfcount.before_command - self._perfcount.k2_start
        self._data.startup_process_time = self._process_time.before_command - self._process_time.k2_start
        logger.debug(
            'Startup (time={t}, process-time={pt})'.format(
                t=self._data.startup_time, pt=self._data.startup_process_time))
        metric('profiling.wall.startup_time', self._data.startup_time)
        metric('profiling.process.startup_time', self._data.startup_process_time)

    @callback_dispatcher([AFTER_COMMAND], [APPLICATION_ENDPOINT])
    @requires(metric='CreateSingleValueMetric')
    def after_command(self, message, metric):
        self._perfcount.after_command = perf_counter()
        self._process_time.after_command = process_time()
        if self._perfcount.before_command is not None:
            self._data.command_execution_time = \
                self._perfcount.after_command - self._perfcount.before_command
        if self._process_time.before_command is not None:
            self._data.command_execution_process_time = \
                self._process_time.after_command - self._process_time.before_command
        logger.debug(
            'Command execution (time={t}, process-time={pt})'.format(
                t=self._data.command_execution_time, pt=self._data.command_execution_process_time))
        metric('profiling.wall.command_execution_time', self._data.command_execution_time)
        metric(
            'profiling.process.command_execution_time', self._data.command_execution_process_time)

    def on_exit(self):
        """
        Triggered after the addon is destroyed.

        Hence, no event-related actions can be done in this or subsequent methods.
        Take extra care what is done.
        """
        self._perfcount.k2_exit = perf_counter()
        self._process_time.k2_exit = process_time()

        self._data.k2_execution_time = self._perfcount.k2_exit - self._perfcount.k2_start
        self._data.k2_execution_process_time = self._process_time.k2_exit - self._process_time.k2_start
        logger.debug(
            'K2 Execution (time={t}, process-time={pt})'.format(
                t=self._data.k2_execution_time, pt=self._data.k2_execution_process_time))
        self.write_reports()

    def write_reports(self):
        """Write all report formats."""
        self.write_csv_report(self._data)
        self.write_json_report(self._data)
        self.write_text_report(self._data)

    def write_csv_report(self, data):
        """Write data to CSV report file, if enabled."""
        if self._report_csv_enabled:
            logger.debug(
                'Writing Profiling CSV report to file {report}'.format(
                    report=self._report_csv_path))
            writer = CsvWriter(self._report_csv_path)
            writer.write(data)

    def write_json_report(self, data):
        """Write data to JSON report file, if enabled."""
        if self._report_json_enabled:
            logger.debug(
                'Writing Profiling JSON report to file {report}'.format(
                    report=self._report_json_path))
            writer = JsonWriter(self._report_json_path)
            writer.write(data)

    def write_text_report(self, data):
        """Write data to text report file, if enabled."""
        if self._report_text_enabled:
            logger.debug(
                'Writing Profiling text report to file {report}'.format(
                    report=self._report_text_path))
            writer = TextWriter(self._report_text_path)
            writer.write(data)
