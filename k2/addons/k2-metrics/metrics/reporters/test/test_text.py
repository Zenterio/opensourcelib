import sys
from unittest import TestCase
from unittest.mock import patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config import ConfigException
from zaf.config.manager import ConfigManager

from metrics import GENERATE_METRICS_REPORT, METRICS_ENDPOINT

from ...metrics import Metric, MetricsNamespace
from ..text import TEXT_DIRECTORY, TEXT_NAMESPACE, TEXT_RENAME_FROM, TEXT_RENAME_TO, \
    TEXT_REPORTER_ID, MetricsTextReporter


class TestMetricsTextReporter(TestCase):

    def test_as_string(self):
        with _create_harness() as harness:
            assert str(harness.extension) == 'MetricsTextReporter(my_metrics_namespace) -> stdout'

    def test_config_options(self):
        with _create_harness() as harness:
            assert harness.extension.namespace == 'my_metrics_namespace'

    def test_rename_from_is_not_valid_regex_raises_config_exception(self):
        with self.assertRaises(ConfigException):
            _create_harness(rename_from='[').__enter__()

    def test_generate_single_value_text_report(self):
        namespace = MetricsNamespace()
        namespace.system_information.decoder_count.store_single(Metric(1, 2))
        namespace.system_information.cpu_count.store_single(Metric(2, 3))

        with _create_harness() as harness:
            with patch.object(harness.extension, '_write_report') as write_mock, \
                    patch('metrics.reporters.text.collect_metrics', return_value=namespace.system_information):
                harness.trigger_event(GENERATE_METRICS_REPORT, METRICS_ENDPOINT, data=None)
                harness.messagebus.wait_for_not_active()

                write_mock.assert_called_with(
                    {
                        'system_information.cpu_count': [3],
                        'system_information.decoder_count': [2]
                    }, sys.stdout)

    def test_generate_series_text_report(self):
        namespace = MetricsNamespace()
        namespace.system_memory.free.store_series(Metric(1, 2))
        namespace.system_memory.free.store_series(Metric(2, 3))
        namespace.system_memory.used.store_series(Metric(3, 4))
        namespace.system_memory.used.store_series(Metric(4, 5))

        with _create_harness() as harness:
            with patch.object(harness.extension, '_write_report') as write_mock, \
                    patch('metrics.reporters.text.collect_metrics', return_value=namespace.system_memory):
                harness.trigger_event(GENERATE_METRICS_REPORT, METRICS_ENDPOINT, data=None)
                harness.messagebus.wait_for_not_active()
                write_mock.assert_called_with(
                    {
                        'system_memory.free': [2, 3],
                        'system_memory.used': [4, 5]
                    }, sys.stdout)

    def test_rename_using_regex(self):
        namespace = MetricsNamespace()
        namespace.part1.name1.store_series(Metric(1, 2))
        namespace.part2.name2.store_series(Metric(1, 2))

        with _create_harness(rename_from=r'part([\d])\.', rename_to=r'hej\1.') as harness:
            with patch.object(harness.extension, '_write_report') as write_mock, \
                    patch('metrics.reporters.text.collect_metrics', return_value=namespace):
                harness.trigger_event(GENERATE_METRICS_REPORT, METRICS_ENDPOINT, data=None)
                harness.messagebus.wait_for_not_active()
                write_mock.assert_called_with({'hej1.name1': [2], 'hej2.name2': [2]}, sys.stdout)


def _create_harness(rename_from=None, rename_to=''):
    config = ConfigManager()
    entity = 'mytextreporter'
    config.set(TEXT_REPORTER_ID, [entity])
    config.set(TEXT_DIRECTORY, 'my/text/directory', entity=entity)
    config.set(TEXT_NAMESPACE, 'my_metrics_namespace', entity=entity)
    config.set(TEXT_RENAME_FROM, rename_from, entity=entity)
    config.set(TEXT_RENAME_TO, rename_to, entity=entity)

    return ExtensionTestHarness(
        MetricsTextReporter,
        config=config,
        endpoints_and_messages={METRICS_ENDPOINT: [GENERATE_METRICS_REPORT]},
    )
