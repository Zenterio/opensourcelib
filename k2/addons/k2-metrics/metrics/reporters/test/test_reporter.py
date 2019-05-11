from unittest import TestCase
from unittest.mock import ANY, MagicMock

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.extensions.extension import FrameworkExtension

from metrics import GENERATE_METRICS_REPORT, METRICS_ENDPOINT

from ..reporter import AbstractMetricsReportExtension


@FrameworkExtension(name='metrics')
class MockAbstractMetricsReportExtension(AbstractMetricsReportExtension):
    handle_generate_metrics_report = MagicMock()


class TestAbstractMetricsReportExtension(TestCase):

    def test_listens_to_generate_metrics_report_events(self):
        with _create_harness() as harness:
            harness.trigger_event(GENERATE_METRICS_REPORT, METRICS_ENDPOINT, data=None)
            harness.messagebus.wait_for_not_active()
            harness.extension.handle_generate_metrics_report.assert_called_with(ANY)


def _create_harness():
    return ExtensionTestHarness(
        MockAbstractMetricsReportExtension,
        endpoints_and_messages={METRICS_ENDPOINT: [GENERATE_METRICS_REPORT]},
    )
