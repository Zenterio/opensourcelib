from unittest import TestCase

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.messages.dispatchers import LocalMessageQueue

from k2.runner.messages import RUNNER_ENDPOINT, TEST_RUN_FINISHED
from metrics import GENERATE_METRICS_REPORT, METRICS_ENDPOINT

from ..triggers import TriggerMetricsReportGenerationOnTestRunFinished


class TestTriggerMetricsReportGenerationOnTestRunFinished(TestCase):

    def test_a_generate_metrics_report_event_is_triggered_on_test_run_finished(self):
        with TestTriggerMetricsReportGenerationOnTestRunFinished._create_harness() as harness:
            with LocalMessageQueue(harness.messagebus, [GENERATE_METRICS_REPORT]) as queue:
                harness.messagebus.trigger_event(TEST_RUN_FINISHED, RUNNER_ENDPOINT, data=None)
                queue.get(timeout=1)

    @staticmethod
    def _create_harness():
        return ExtensionTestHarness(
            TriggerMetricsReportGenerationOnTestRunFinished,
            endpoints_and_messages={
                METRICS_ENDPOINT: [GENERATE_METRICS_REPORT],
                RUNNER_ENDPOINT: [TEST_RUN_FINISHED]
            },
        )
