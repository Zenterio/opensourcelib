"""Generate a `TestNG <http://testng.org/doc/>`_ compatible XML report with the test results."""

import logging
import os

from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.reports.testng import REPORTS_TESTNG, REPORTS_TESTNG_FILE
from k2.results import RESULTS_ENDPOINT, TEST_RESULTS_COLLECTED

from . import writer

logger = logging.getLogger(get_logger_name('k2', 'testngreport'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='testngreport',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(REPORTS_TESTNG, required=False),
        ConfigOption(REPORTS_TESTNG_FILE, required=False),
    ],
    groups=['test-results'],
    activate_on=[REPORTS_TESTNG],
)
class TestNgReporter(AbstractExtension):
    """Generates TestNG report."""

    def __init__(self, config, instances):
        self._enabled = config.get(REPORTS_TESTNG, False)
        if self._enabled:
            self._report_file = config.get(REPORTS_TESTNG_FILE, None)

    @callback_dispatcher([TEST_RESULTS_COLLECTED], [RESULTS_ENDPOINT])
    def handle_message(self, message):
        dir = os.path.dirname(self._report_file)
        if dir != '' and not os.path.exists(dir):
            os.makedirs(dir)
        logger.info('Writing TestNG XML report to file %s', self._report_file)

        if message.data:
            writer.write_testng_report(message.data, self._report_file)
        else:
            logger.warning(
                'Test result data is empty. Will not generate TestNG report', self._report_file)
