"""Generate a JUnit compatible XML report with the test results."""

import logging
import os

from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.reports.junit import REPORTS_JUNIT, REPORTS_JUNIT_FILE
from k2.results import RESULTS_ENDPOINT, TEST_RESULTS_COLLECTED

from . import writer

logger = logging.getLogger(get_logger_name('k2', 'junitreport'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='junitreport',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(REPORTS_JUNIT, required=False),
        ConfigOption(REPORTS_JUNIT_FILE, required=False),
    ],
    groups=['test-results'],
    activate_on=[REPORTS_JUNIT],
)
class JUnitReporter(AbstractExtension):
    """Generates JUnit report."""

    def __init__(self, config, instances):
        self._enabled = config.get(REPORTS_JUNIT, False)
        if self._enabled:
            self._report_file = config.get(REPORTS_JUNIT_FILE, None)

    @callback_dispatcher([TEST_RESULTS_COLLECTED], [RESULTS_ENDPOINT])
    def handle_message(self, message):
        dir = os.path.dirname(self._report_file)
        if dir != '' and not os.path.exists(dir):
            os.makedirs(dir)
        logger.info('Writing JUnit XML report to file %s', self._report_file)

        if message.data:
            writer.write_junit_report(message.data, self._report_file)
        else:
            logger.warning(
                'Test result data is empty. Will not generate JUnit report', self._report_file)
