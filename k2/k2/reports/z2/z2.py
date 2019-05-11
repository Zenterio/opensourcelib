"""
Generate a Z2 compatible JSON formatted report of test results.

The resulting report can be written to disk and optionally uploaded to a remote Z2 server.
"""

import logging

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.reports.z2 import Z2_INTERNAL_PUBLISH_REPORT_REQUEST, Z2_REPORTS, Z2_REPORTS_BUILD_NUMBER, \
    Z2_REPORTS_ENDPOINT, Z2_REPORTS_FILE, Z2_REPORTS_JOB_NAME, Z2_REPORTS_URL
from k2.reports.z2.writer import generate_report, upload_report, write_report
from k2.results import RESULTS_ENDPOINT, TEST_RESULTS_COLLECTED

logger = logging.getLogger(get_logger_name('k2', 'z2report'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='z2report',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(Z2_REPORTS, required=True),
        ConfigOption(Z2_REPORTS_JOB_NAME, required=False),
        ConfigOption(Z2_REPORTS_BUILD_NUMBER, required=False),
    ],
    endpoints_and_messages={
        Z2_REPORTS_ENDPOINT: [Z2_INTERNAL_PUBLISH_REPORT_REQUEST],
    },
    groups=['test-results'],
    activate_on=[Z2_REPORTS],
)
class ReportGenerator(AbstractExtension):
    """Generate a Z2 report."""

    def __init__(self, config, instances):
        self._job_name = config.get(Z2_REPORTS_JOB_NAME, None)
        self._build_number = config.get(Z2_REPORTS_BUILD_NUMBER, None)

    @callback_dispatcher([TEST_RESULTS_COLLECTED], [RESULTS_ENDPOINT])
    @requires(messagebus='MessageBus')
    def handle_message(self, message, messagebus):
        report = generate_report(message.data, self._job_name, self._build_number)

        logger.info('Publishing Z2 report')
        futures = messagebus.send_request(
            Z2_INTERNAL_PUBLISH_REPORT_REQUEST, Z2_REPORTS_ENDPOINT, data=report)
        for future in futures.as_completed():
            try:
                future.result()
            except Exception as e:
                msg = 'Could not publish Z2 report: {reason}'.format(reason=str(e))
                logger.debug(msg, exc_info=True)
                logger.error(msg)
                raise
        logger.info('Published Z2 report')


@CommandExtension(
    name='z2report',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(Z2_REPORTS, required=True),
        ConfigOption(Z2_REPORTS_FILE, required=True),
    ],
    groups=['test-results'],
    activate_on=[Z2_REPORTS],
)
class FileReporter(AbstractExtension):
    """Writes Z2 reports to file on disk."""

    def __init__(self, config, instances):
        self._report_file = config.get(Z2_REPORTS_FILE)

    @callback_dispatcher([Z2_INTERNAL_PUBLISH_REPORT_REQUEST], [Z2_REPORTS_ENDPOINT])
    def handle_publish_report_request(self, message):
        write_report(message.data, self._report_file)


@CommandExtension(
    name='z2report',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(Z2_REPORTS, required=True),
        ConfigOption(Z2_REPORTS_URL, required=False),
    ],
    groups=['test-results'],
    activate_on=[Z2_REPORTS, Z2_REPORTS_URL],
)
class UploadReporter(AbstractExtension):
    """Uploads Z2 reports to a remote Z2 server."""

    def __init__(self, config, instances):
        self._url = config.get(Z2_REPORTS_URL)

    @callback_dispatcher([Z2_INTERNAL_PUBLISH_REPORT_REQUEST], [Z2_REPORTS_ENDPOINT])
    def handle_publish_report_request(self, message):
        try:
            upload_report(message.data, self._url)
        except Exception:
            pass
