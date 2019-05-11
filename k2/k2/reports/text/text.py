"""
Generate a text reports of test results to command line and/or file in a human readable format.

The text report can be generated in multiple formats

summary:
    Summary with number of testcase with each verdict.

brief:
    Summary + detailed information about failures

full:
    Brief + verdict and duration for all test cases.
"""
import logging

from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.reports.text import REPORTS_TEXT, REPORTS_TEXT_OUTPUT, REPORTS_TEXT_SHOW_OWNER, \
    REPORTS_TEXT_TEMPLATE
from k2.results import RESULTS_ENDPOINT, TEST_RESULTS_COLLECTED

from . import writer

logger = logging.getLogger(get_logger_name('k2', 'textreport'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='textreport',
    config_options=[
        ConfigOption(REPORTS_TEXT, required=True),
        ConfigOption(REPORTS_TEXT_OUTPUT, required=False),
        ConfigOption(REPORTS_TEXT_SHOW_OWNER, required=True),
        ConfigOption(REPORTS_TEXT_TEMPLATE, required=True),
    ],
    extends=[RUN_COMMAND],
    groups=['test-results'],
    activate_on=[REPORTS_TEXT],
)
class TextReporter(AbstractExtension):
    """Generate text reports."""

    def __init__(self, config, instances):
        self._output = set()
        self._output.update(config.get(REPORTS_TEXT_OUTPUT, ['-']))
        self._template = config.get(REPORTS_TEXT_TEMPLATE, 'full')
        self._show_owner = config.get(REPORTS_TEXT_SHOW_OWNER)

    @callback_dispatcher([TEST_RESULTS_COLLECTED], [RESULTS_ENDPOINT])
    def handle_message(self, message):
        writer.write_report(message.data, self._output, self._template, self._show_owner)
