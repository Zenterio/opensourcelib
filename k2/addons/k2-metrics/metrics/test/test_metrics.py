import re
from unittest import TestCase
from unittest.mock import ANY, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from ..messages import collect_metrics, create_series_metric, create_single_value_metric
from ..metrics import CREATE_METRIC, METRICS_ENDPOINT, WRITE_TO_LOG_ON_EXIT, \
    FlatMetricsNamespaceDataView, Metric, Metrics, MetricsNamespace


class TestMetric(TestCase):

    def test_store_timestamp_and_data(self):
        metric = Metric('my_timestamp', 'my_data')
        assert metric.timestamp == 'my_timestamp'
        assert metric.data == 'my_data'
        assert metric.tags is None

    def test_tagged_metric(self):
        metric = Metric(ANY, ANY, ['a_tag', 'another_tag'])
        assert ['a_tag', 'another_tag'] == metric.tags

    def test_raises_type_error_if_tags_are_non_iterable(self):
        with self.assertRaises(TypeError):
            non_iterable = 3
            Metric(ANY, ANY, non_iterable)


class TestMetricsNamespace(TestCase):

    def setUp(self):
        self.mn = MetricsNamespace()

    def test_add_a_single_value_metric(self):
        a = Metric(1, 'a')
        self.mn.store_single(a)
        assert [a] == list(self.mn)

    def test_override_a_single_value_metric(self):
        a = Metric(1, 'a')
        b = Metric(2, 'b')
        self.mn.store_single(a)
        self.mn.store_single(b)
        assert [b] == list(self.mn)

    def test_add_a_series_metric(self):
        a = Metric(1, 'a')
        self.mn.store_series(a)
        assert [a] == list(self.mn)

    def test_add_multiple_series_metric(self):
        a = Metric(1, 'a')
        b = Metric(2, 'b')
        self.mn.store_series(a)
        self.mn.store_series(b)
        assert [a, b] == list(self.mn)

    def test_nested_namespaces(self):
        a = Metric(1, 'a')
        b = Metric(2, 'b')
        c = Metric(3, 'c')
        self.mn.a.a.store_series(a)
        self.mn.a.a.store_series(b)
        self.mn.a.b.store_series(c)
        assert [self.mn.a.a, self.mn.a.b] == list(self.mn.a)
        assert [a, b] == list(self.mn.a.a)
        assert [c] == list(self.mn.a.b)

    def test_empty_namespace(self):
        assert len(list(self.mn.a)) == 0

    def test_series_are_stored_in_order(self):
        for i in range(10):
            self.mn.store_series(Metric(1, i))
        assert list(range(10)) == [metric.data for metric in self.mn]

    def test_can_not_override_a_single_value_with_a_series(self):
        a = Metric(1, 'a')
        self.mn.store_single(a)
        with self.assertRaises(ValueError):
            self.mn.store_series(a)

    def test_can_not_override_a_series_with_a_single_value(self):
        a = Metric(1, 'a')
        self.mn.store_series(a)
        with self.assertRaises(ValueError):
            self.mn.store_single(a)

    def test_raises_if_storing_series_in_non_leaf_namespace(self):
        a = Metric(1, 'a')
        self.mn.a.b.c.store_series(a)
        with self.assertRaises(TypeError):
            self.mn.a.b.store_series(a)

    def test_raises_if_storing_single_value_in_non_leaf_namespace(self):
        a = Metric(1, 'a')
        self.mn.a.b.c.store_series(a)
        with self.assertRaises(TypeError):
            self.mn.a.b.store_single(a)

    def test_is_leaf(self):
        self.mn.a.b.store_single(Metric(1, 'a'))
        assert not self.mn.is_leaf
        assert not self.mn.a.is_leaf
        assert self.mn.a.b.is_leaf

    def test_name(self):
        self.mn.a.b.store_single(Metric(1, 'a'))
        assert self.mn.a.name == 'a'
        assert self.mn.b.name == 'b'

    def test_children(self):
        self.mn.a.b.c.store_single(Metric(1, 'a'))
        self.mn.a.b.d.store_single(Metric(2, 'b'))
        assert len(self.mn.a.children) == 1
        assert len(self.mn.a.b.children) == 2
        assert len(self.mn.a.b.c.children) == 0
        assert len(self.mn.a.b.d.children) == 0


class TestFlatMetricsNamespaceDataView(TestCase):

    def test_flat_single_metrics_view(self):
        ns = MetricsNamespace()
        ns.a.b.store_single(Metric(None, 1))
        ns.a.c.store_single(Metric(None, 2))
        data = FlatMetricsNamespaceDataView(ns.a).get_data()
        assert data['a.b'] == [1]
        assert data['a.c'] == [2]

    def test_flat_series_metrics_view(self):
        ns = MetricsNamespace()
        ns.a.b.store_series(Metric(None, 1))
        ns.a.b.store_series(Metric(None, 2))
        data = FlatMetricsNamespaceDataView(ns.a).get_data()
        assert data['a.b'] == [1, 2]

    def test_view_leaf(self):
        ns = MetricsNamespace()
        ns.a.b.store_series(Metric(None, 1))
        ns.a.b.store_series(Metric(None, 2))
        data = FlatMetricsNamespaceDataView(ns.a.b).get_data()
        assert data['a.b'] == [1, 2]

    def test_filter_keys(self):
        ns = MetricsNamespace()
        ns.a.b.store_series(Metric(None, 1))
        ns.a.c.store_series(Metric(None, 2))
        data = FlatMetricsNamespaceDataView(ns.a, key_filter=lambda key: 'b' in key).get_data()
        assert data['a.b'] == [1]

    def test_extended_to_qualified_names(self):
        ns = MetricsNamespace()
        ns.a.b.c.d.e.f.store_series(Metric(None, 1))
        data = FlatMetricsNamespaceDataView(ns.a.b.c).get_data()
        assert data['a.b.c.d.e.f'] == [1]

    def test_rename_of_keys(self):
        ns = MetricsNamespace()
        ns.a.b.c.d.e.f.store_series(Metric(None, 1))
        data = FlatMetricsNamespaceDataView(
            ns.a.b.c,
            rename_regex=re.compile('(?P<b_or_e>[be])'),
            rename_to=r'\g<b_or_e>\g<b_or_e>').get_data()
        assert data['a.bb.c.d.ee.f'] == [1]

    def test_that_rename_can_be_called_with_string_instead_of_compiled_regex(self):
        ns = MetricsNamespace()
        ns.a.b.c.d.e.f.store_series(Metric(None, 1))
        data = FlatMetricsNamespaceDataView(
            ns.a.b.c, rename_regex='(?P<b_or_e>[be])',
            rename_to=r'\g<b_or_e>\g<b_or_e>').get_data()
        assert data['a.bb.c.d.ee.f'] == [1]


class TestMetricsExtension(TestCase):

    def test_metrics_extension_listens_to_store_metric_events(self):
        with _create_harness() as harness:
            assert harness.any_registered_dispatchers(CREATE_METRIC, METRICS_ENDPOINT)

    def test_registering_a_single_value_metric(self):
        with _create_harness() as harness:
            with harness.patch('metrics.metrics.MetricsNamespace.store_single') as store:
                futures = create_single_value_metric(harness.messagebus, 'my_namespace', 'my_data')
                futures.wait()
                store.assert_called_with(Metric(ANY, 'my_data', tags=None))

    def test_registering_a_series_metric(self):
        with _create_harness() as harness:
            with harness.patch('metrics.metrics.MetricsNamespace.store_series') as store:
                futures = create_series_metric(harness.messagebus, 'my_namespace', 'my_data')
                futures.wait()
                store.assert_called_with(Metric(ANY, 'my_data', tags=None))

    def test_regestering_a_tagged_metric(self):
        with _create_harness() as harness:
            with harness.patch('metrics.metrics.MetricsNamespace.store_series') as store:
                futures = create_series_metric(
                    harness.messagebus, 'my_namespace', 'my_data', ['my_tag'])
                futures.wait()
                store.assert_called_with(Metric(ANY, 'my_data', tags=['my_tag']))

    def test_collect_missing_metrics(self):
        with _create_harness() as harness:
            metrics = collect_metrics(harness.messagebus, 'my_namespace')
            assert len(list(metrics)) == 0

    def test_collect_registered_metrics(self):
        with _create_harness() as harness:
            futures = create_series_metric(harness.messagebus, 'my_namespace', 'my_data')
            futures += create_series_metric(
                harness.messagebus, 'my_other_namespace', 'my_other_data')
            futures.wait()

            my_namespace = list(collect_metrics(harness.messagebus, 'my_namespace'))
            assert len(my_namespace) == 1
            assert my_namespace[0].data == 'my_data'

            my_other_namespace = list(collect_metrics(harness.messagebus, 'my_other_namespace'))
            assert len(my_other_namespace) == 1
            assert my_other_namespace[0].data == 'my_other_data'

    @patch('metrics.metrics.logger.debug')
    def test_writes_to_log_if_active(self, debug_logger):
        with _create_harness(config={WRITE_TO_LOG_ON_EXIT: True}):
            pass
        debug_logger.assert_called_with('Metrics Done')

    @patch('metrics.metrics.logger.debug')
    def test_does_not_write_to_log_if_deactive(self, debug_logger):
        with _create_harness(config={WRITE_TO_LOG_ON_EXIT: False}):
            pass
        self.assertEqual(debug_logger.call_count, 0)


def _create_harness(config=None):
    config_manager = ConfigManager()
    for id, value in config.items() if config else []:
        config_manager.set(id, value)
    return ExtensionTestHarness(Metrics, config=config_manager, endpoints_and_messages={})
