import logging

from zaf.component.decorator import requires
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND
from k2.runner.messages import TEST_RUN_FINISHED
from metrics import GENERATE_METRICS_AGGREGATE, GENERATE_METRICS_REPORT, METRICS_ENDPOINT

logger = logging.getLogger(get_logger_name('k2', 'metrics', 'triggers'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='metrics',
    extends=[RUN_COMMAND],
    groups=['metrics'],
)
class TriggerMetricsReportGenerationOnTestRunFinished(AbstractExtension):
    """Triggers metrics reports generation when a test run is finished."""

    @callback_dispatcher([TEST_RUN_FINISHED], priority=-1)
    @requires(messagebus='MessageBus')
    def trigger_report_generation(self, message, messagebus):
        logger.info('Test run finished, triggering metrics report generation')
        messagebus.trigger_event(GENERATE_METRICS_REPORT, METRICS_ENDPOINT, data=None)


@CommandExtension(
    name='metrics',
    extends=[RUN_COMMAND],
    groups=['metrics'],
)
class TriggerMetricsAggregatesGenerationOnTestRunFinished(AbstractExtension):
    """Triggers metrics aggregates generation when a test run is finished."""

    @callback_dispatcher([TEST_RUN_FINISHED], priority=1)
    @requires(messagebus='MessageBus')
    def trigger_aggregates_generation(self, message, messagebus):
        logger.info('Test run finished, triggering metrics aggregates generation')
        messagebus.trigger_event(GENERATE_METRICS_AGGREGATE, METRICS_ENDPOINT, data=None)
