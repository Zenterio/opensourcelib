import os
from io import StringIO
from unittest import TestCase

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config import ConfigException
from zaf.config.manager import ConfigManager

from metrics import GENERATE_METRICS_REPORT, METRICS_ENDPOINT

from ...metrics import Metric, MetricsNamespace
from ..csv import CSV_DIRECTORY, CSV_FILENAME, CSV_NAMESPACE, CSV_RENAME_FROM, CSV_RENAME_TO, \
    CSV_REPORTER_ID, MetricsCsvReporter


class TestMetricsCsvReporter(TestCase):

    def test_as_string(self):
        with _create_harness() as harness:
            assert str(
                harness.extension) == 'MetricsCsvReporter(my_metrics_namespace) -> myreport.csv'

    def test_config_options(self):
        with _create_harness() as harness:
            assert harness.extension.writer._path == os.path.join(
                'my/csv/directory', 'myreport.csv')
            assert harness.extension.namespace == 'my_metrics_namespace'

    def test_rename_from_is_not_valid_regex_raises_config_exception(self):
        with self.assertRaises(ConfigException):
            _create_harness(rename_from='[').__enter__()

    def test_generate_single_value_csv_report(self):
        namespace = MetricsNamespace()
        namespace.system_information.decoder_count.store_single(Metric(1, 2))
        namespace.system_information.cpu_count.store_single(Metric(2, 3))

        with _create_harness() as harness:
            stream = StringIO()
            harness.extension.writer.write = \
                lambda data: harness.extension.writer.write_to_stream(data, stream)
            harness.extension._get_namespace = lambda: namespace.system_information
            harness.trigger_event(GENERATE_METRICS_REPORT, METRICS_ENDPOINT, data=None)
            harness.messagebus.wait_for_not_active()
            expected = 'system_information.cpu_count,system_information.decoder_count\r\n3,2\r\n'
            assert expected == stream.getvalue()

    def test_generate_series_csv_report(self):
        namespace = MetricsNamespace()
        namespace.system_memory.free.store_series(Metric(1, 2))
        namespace.system_memory.free.store_series(Metric(2, 3))
        namespace.system_memory.used.store_series(Metric(3, 4))
        namespace.system_memory.used.store_series(Metric(4, 5))

        with _create_harness() as harness:
            stream = StringIO()
            harness.extension.writer.write = \
                lambda data: harness.extension.writer.write_to_stream(data, stream)
            harness.extension._get_namespace = lambda: namespace.system_memory
            harness.trigger_event(GENERATE_METRICS_REPORT, METRICS_ENDPOINT, data=None)
            harness.messagebus.wait_for_not_active()
            expected = 'system_memory.free,system_memory.used\r\n2,4\r\n3,5\r\n'
            assert expected == stream.getvalue()

    def test_rename_using_regex(self):
        namespace = MetricsNamespace()
        namespace.part1.name1.store_series(Metric(1, 2))
        namespace.part2.name2.store_series(Metric(1, 2))

        with _create_harness(rename_from=r'part([\d])\.', rename_to=r'hej\1.') as harness:
            stream = StringIO()
            harness.extension.writer.write = \
                lambda data: harness.extension.writer.write_to_stream(data, stream)
            harness.extension._get_namespace = lambda: namespace
            harness.trigger_event(GENERATE_METRICS_REPORT, METRICS_ENDPOINT, data=None)
            harness.messagebus.wait_for_not_active()
            expected = 'hej1.name1,hej2.name2\r\n2,2\r\n'
            assert expected == stream.getvalue()


def _create_harness(rename_from=None, rename_to=''):
    config = ConfigManager()
    entity = 'mycsvreporter'
    config.set(CSV_REPORTER_ID, [entity])
    config.set(CSV_DIRECTORY, 'my/csv/directory', entity=entity)
    config.set(CSV_FILENAME, 'myreport.csv', entity=entity)
    config.set(CSV_NAMESPACE, 'my_metrics_namespace', entity=entity)
    config.set(CSV_RENAME_FROM, rename_from, entity=entity)
    config.set(CSV_RENAME_TO, rename_to, entity=entity)

    return ExtensionTestHarness(
        MetricsCsvReporter,
        config=config,
        endpoints_and_messages={METRICS_ENDPOINT: [GENERATE_METRICS_REPORT]},
    )
