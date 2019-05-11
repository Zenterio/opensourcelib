from unittest import TestCase
from unittest.mock import Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager

from metrics import GENERATE_METRICS_AGGREGATE, METRICS_ENDPOINT

from ...metrics import Metric, MetricsNamespace
from ..series import SERIES_AGGREGATOR_IDS, SERIES_AGGREGATOR_TYPE, SOURCE_SERIES, TARGET_VALUE, \
    MetricsSeriesAggregator


class TestMetricsSeriesAggregator(TestCase):

    @staticmethod
    def _create_harness(source_series, target_value, type):
        config = ConfigManager()
        entity = 'myaggregator'
        config.set(SERIES_AGGREGATOR_IDS, [entity])
        config.set(SOURCE_SERIES, source_series, entity=entity)
        config.set(TARGET_VALUE, target_value, entity=entity)
        config.set(SERIES_AGGREGATOR_TYPE, type, entity=entity)

        create_single_value_metric = Mock()
        harness = ExtensionTestHarness(
            MetricsSeriesAggregator,
            config=config,
            endpoints_and_messages={METRICS_ENDPOINT: [GENERATE_METRICS_AGGREGATE]},
            components=[
                ComponentMock(name='CreateSingleValueMetric', mock=create_single_value_metric),
            ])
        harness.create_single_value_metric = create_single_value_metric
        return harness

    def test_config_options(self):
        with TestMetricsSeriesAggregator._create_harness(source_series=['source_series'],
                                                         target_value='target_value',
                                                         type='min') as harness:
            assert harness.extension._entity == 'myaggregator'
            assert harness.extension._source_series == ('source_series', )
            assert harness.extension._target_value == 'target_value'
            assert harness.extension._type == 'min'

    def test_minimum_aggregate_a_series_with_one_value(self):
        namespace = MetricsNamespace()
        namespace.data.values.store_series(Metric(1, 1))

        with TestMetricsSeriesAggregator._create_harness(source_series=['data.values'],
                                                         target_value='data.stats.minimum',
                                                         type='min') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data.values
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_called_once_with('data.stats.minimum', 1)

    def test_minimum_aggregate_a_series_with_multiple_values(self):
        namespace = MetricsNamespace()
        namespace.data.values.store_series(Metric(1, 2))
        namespace.data.values.store_series(Metric(1, 3))

        with TestMetricsSeriesAggregator._create_harness(source_series=['data.values'],
                                                         target_value='data.stats.minimum',
                                                         type='min') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data.values
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_called_once_with('data.stats.minimum', 2)

    def test_minimum_aggregate_a_series_with_no_values(self):
        namespace = MetricsNamespace()

        with TestMetricsSeriesAggregator._create_harness(source_series=['data.values'],
                                                         target_value='data.stats.minimum',
                                                         type='min') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data.values
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_not_called()

    def test_minimum_aggregate_multiple_series(self):
        namespace = MetricsNamespace()
        namespace.data.some_values.store_series(Metric(1, 2))
        namespace.data.some_values.store_series(Metric(1, 3))
        namespace.data.some_other_values.store_series(Metric(1, 7))
        namespace.data.some_other_values.store_series(Metric(1, 1))

        with TestMetricsSeriesAggregator._create_harness(
                source_series=['data'], target_value='data.stats.minimum', type='min') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_called_once_with('data.stats.minimum', 1)

    def test_maximum_aggregate_a_series_with_one_value(self):
        namespace = MetricsNamespace()
        namespace.data.values.store_series(Metric(1, 1))

        with TestMetricsSeriesAggregator._create_harness(source_series=['data.values'],
                                                         target_value='data.stats.maximum',
                                                         type='max') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data.values
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_called_once_with('data.stats.maximum', 1)

    def test_maximum_aggregate_a_series_with_multiple_values(self):
        namespace = MetricsNamespace()
        namespace.data.values.store_series(Metric(1, 2))
        namespace.data.values.store_series(Metric(1, 3))

        with TestMetricsSeriesAggregator._create_harness(source_series=['data.values'],
                                                         target_value='data.stats.maximum',
                                                         type='max') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data.values
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_called_once_with('data.stats.maximum', 3)

    def test_maximum_aggregate_a_series_with_no_values(self):
        namespace = MetricsNamespace()

        with TestMetricsSeriesAggregator._create_harness(source_series=['data.values'],
                                                         target_value='data.stats.maximum',
                                                         type='max') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data.values
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_not_called()

    def test_maximum_aggregate_multiple_series(self):
        namespace = MetricsNamespace()
        namespace.data.some_values.store_series(Metric(1, 2))
        namespace.data.some_values.store_series(Metric(1, 3))
        namespace.data.some_other_values.store_series(Metric(1, 7))
        namespace.data.some_other_values.store_series(Metric(1, 1))

        with TestMetricsSeriesAggregator._create_harness(
                source_series=['data'], target_value='data.stats.maximum', type='max') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_called_once_with('data.stats.maximum', 7)

    def test_average_aggregate_a_series_with_one_value(self):
        namespace = MetricsNamespace()
        namespace.data.values.store_series(Metric(1, 1))

        with TestMetricsSeriesAggregator._create_harness(source_series=['data.values'],
                                                         target_value='data.stats.average',
                                                         type='average') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data.values
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_called_once_with('data.stats.average', 1)

    def test_average_aggregate_a_series_with_multiple_values(self):
        namespace = MetricsNamespace()
        namespace.data.values.store_series(Metric(1, 0))
        namespace.data.values.store_series(Metric(1, 10))

        with TestMetricsSeriesAggregator._create_harness(source_series=['data.values'],
                                                         target_value='data.stats.average',
                                                         type='average') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data.values
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_called_once_with('data.stats.average', 5)

    def test_average_aggregate_a_series_with_no_values(self):
        namespace = MetricsNamespace()

        with TestMetricsSeriesAggregator._create_harness(source_series=['data.values'],
                                                         target_value='data.stats.average',
                                                         type='average') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data.values
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_not_called()

    def test_average_aggregate_multiple_series(self):
        namespace = MetricsNamespace()
        namespace.data.some_values.store_series(Metric(1, 20))
        namespace.data.some_values.store_series(Metric(1, 30))
        namespace.data.some_other_values.store_series(Metric(1, 24))
        namespace.data.some_other_values.store_series(Metric(1, 26))

        with TestMetricsSeriesAggregator._create_harness(source_series=['data'],
                                                         target_value='data.stats.average',
                                                         type='average') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_called_once_with('data.stats.average', 25)

    def test_aggregateq_multiple_series(self):
        namespace = MetricsNamespace()
        namespace.data.values.store_series(Metric(1, 0))
        namespace.data.values.store_series(Metric(1, 10))

        with TestMetricsSeriesAggregator._create_harness(source_series=['a', 'b'],
                                                         target_value='data.stats.average',
                                                         type='average') as harness:
            harness.extension._get_namespace = lambda a, b: namespace.data
            harness.messagebus.send_request(GENERATE_METRICS_AGGREGATE)

        harness.create_single_value_metric.assert_called_once_with('data.stats.average', 5)
