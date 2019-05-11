import os
from io import StringIO
from textwrap import dedent
from unittest import TestCase

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from metrics import GENERATE_METRICS_REPORT, METRICS_ENDPOINT

from ...metrics import Metric, MetricsNamespace
from ..json import JSON_DIRECTORY, JSON_FILENAME, JSON_NAMESPACE, JSON_REPORTER_ID, \
    MetricsJsonReporter


class TestMetricsJsonReporter(TestCase):

    def test_as_string(self):
        with _create_harness() as harness:
            assert str(
                harness.extension) == 'MetricsJsonReporter(my_metrics_namespace) -> myreport.json'

    def test_config_options(self):
        with _create_harness() as harness:
            assert harness.extension.writer._path == os.path.join(
                'my/json/directory', 'myreport.json')
            assert harness.extension.namespace == 'my_metrics_namespace'

    def test_generate_json_report(self):
        namespace = MetricsNamespace()
        namespace.system_memory.used.store_series(Metric(1, 199905))
        namespace.system_memory.used.store_series(Metric(2, 5))
        namespace.system_memory.used.store_series(Metric(3, 199901))
        namespace.system_memory.free.store_series(Metric(1, 100))
        namespace.system_memory.free.store_series(Metric(2, 200000, ['zids.bin crashed!']))
        namespace.system_memory.free.store_series(Metric(3, 99, ['everything is back to normal']))
        namespace.system_memory.total.store_single(Metric(1, 200005))

        with _create_harness() as harness:
            stream = StringIO()
            harness.extension.writer.write = \
                lambda data: harness.extension.writer.write_to_stream(data, stream)
            harness.extension._get_namespace = lambda: namespace
            harness.trigger_event(GENERATE_METRICS_REPORT, METRICS_ENDPOINT, data=None)
            harness.messagebus.wait_for_not_active()
            expected = dedent(
                """\
            {
                "system_memory": {
                    "used": [
                        {
                            "timestamp": 1,
                            "data": 199905,
                            "tags": null
                        },
                        {
                            "timestamp": 2,
                            "data": 5,
                            "tags": null
                        },
                        {
                            "timestamp": 3,
                            "data": 199901,
                            "tags": null
                        }
                    ],
                    "free": [
                        {
                            "timestamp": 1,
                            "data": 100,
                            "tags": null
                        },
                        {
                            "timestamp": 2,
                            "data": 200000,
                            "tags": [
                                "zids.bin crashed!"
                            ]
                        },
                        {
                            "timestamp": 3,
                            "data": 99,
                            "tags": [
                                "everything is back to normal"
                            ]
                        }
                    ],
                    "total": {
                        "timestamp": 1,
                        "data": 200005,
                        "tags": null
                    }
                }
            }""")
            actual = stream.getvalue()
            assert actual == expected


def _create_harness():
    config = ConfigManager()
    entity = 'myjsonreporter'
    config.set(JSON_REPORTER_ID, [entity])
    config.set(JSON_DIRECTORY, 'my/json/directory', entity=entity)
    config.set(JSON_FILENAME, 'myreport.json', entity=entity)
    config.set(JSON_NAMESPACE, 'my_metrics_namespace', entity=entity)

    return ExtensionTestHarness(
        MetricsJsonReporter,
        config=config,
        endpoints_and_messages={METRICS_ENDPOINT: [GENERATE_METRICS_REPORT]},
    )
