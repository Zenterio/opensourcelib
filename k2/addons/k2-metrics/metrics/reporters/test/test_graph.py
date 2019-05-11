from unittest import TestCase

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from metrics import GENERATE_METRICS_REPORT, METRICS_ENDPOINT
from metrics.reporters.graph import GRAPH_DIRECTORY

from ...metrics import Metric, MetricsNamespace
from ..graph import GRAPH_FILENAME, GRAPH_NAMESPACE, GRAPH_REPORTER_ID, GRAPH_TITLE, GRAPH_YLABEL, \
    GRAPH_YMAX, GRAPH_YMIN, MetricsGraphReporter


class TestMetricsGraphReporter(TestCase):

    def test_as_string(self):
        with _create_harness() as harness:
            assert str(
                harness.extension) == 'MetricsGraphReporter(my_metrics_namespace) -> myreport.png'

    def test_config_options(self):
        with _create_harness() as harness:
            assert harness.extension.filename == 'myreport.png'
            assert harness.extension.namespaces == ('my_metrics_namespace', )
            assert harness.extension.title == 'my_graph_title'
            assert harness.extension.ylabel == 'my_graph_ylabel'
            assert harness.extension.ymin == 1.0
            assert harness.extension.ymax == 2.0

    def test_generate_graph_report(self):
        namespace = MetricsNamespace()
        namespace.system_memory.free.store_series(Metric(1, 100))
        namespace.system_memory.free.store_series(Metric(2, 200000))
        namespace.system_memory.free.store_series(Metric(3, 99))

        with _create_harness() as harness:
            harness.extension._write_to_disk = lambda: None
            harness.extension._get_namespaces = lambda: \
                {'system_memory.free': namespace.system_memory.free}
            harness.trigger_event(GENERATE_METRICS_REPORT, METRICS_ENDPOINT, data=None)
            harness.messagebus.wait_for_not_active()


def _create_harness():
    config = ConfigManager()
    entity = 'mygraphreporter'
    config.set(GRAPH_REPORTER_ID, [entity])
    config.set(GRAPH_DIRECTORY, 'my/graph/directory', entity=entity)
    config.set(GRAPH_FILENAME, 'myreport.png', entity=entity)
    config.set(GRAPH_NAMESPACE, ('my_metrics_namespace', ), entity=entity)
    config.set(GRAPH_TITLE, 'my_graph_title', entity=entity)
    config.set(GRAPH_YLABEL, 'my_graph_ylabel', entity=entity)
    config.set(GRAPH_YMIN, 1.0, entity=entity)
    config.set(GRAPH_YMAX, 2.0, entity=entity)

    return ExtensionTestHarness(
        MetricsGraphReporter,
        config=config,
        endpoints_and_messages={METRICS_ENDPOINT: [GENERATE_METRICS_REPORT]},
    )
