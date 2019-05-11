import logging
import os

from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import FrameworkExtension, get_logger_name

from k2.utils.writers import JsonWriter

from ..messages import collect_metrics
from .reporter import AbstractMetricsReportExtension

logger = logging.getLogger(get_logger_name('k2', 'metrics.json'))
logger.addHandler(logging.NullHandler())

JSON_REPORTER_ID = ConfigOptionId(
    name='ids',
    description='Names a JSON metrics reporter instance',
    multiple=True,
    entity=True,
    namespace='metrics.json',
)

JSON_DIRECTORY = ConfigOptionId(
    name='dir',
    description='Directory to write the JSON reports to',
    default='${output.dir}/metrics/json',
    at=JSON_REPORTER_ID,
)

JSON_FILENAME = ConfigOptionId(
    name='filename',
    description='Name of the JSON file to write',
    at=JSON_REPORTER_ID,
)

JSON_NAMESPACE = ConfigOptionId(
    name='namespace',
    description='The metrics namespace to report',
    at=JSON_REPORTER_ID,
)


@FrameworkExtension(
    name='metrics',
    config_options=[
        ConfigOption(JSON_REPORTER_ID, required=False, instantiate_on=True),
        ConfigOption(JSON_DIRECTORY, required=True),
        ConfigOption(JSON_FILENAME, required=True),
        ConfigOption(JSON_NAMESPACE, required=True),
    ],
    groups=['metrics'],
)
class MetricsJsonReporter(AbstractMetricsReportExtension):
    """
    Metrics reporter that writes JSON formatted reports.

    Example report:

    .. code-block:: json

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
                        "data": 20000,
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
        }

    """

    def __init__(self, config, instances):
        super().__init__(config, instances)
        self.filename = config.get(JSON_FILENAME)
        self.writer = JsonWriter(os.path.join(config.get(JSON_DIRECTORY), self.filename))
        self.namespace = config.get(JSON_NAMESPACE)

    def __str__(self):
        return 'MetricsJsonReporter({namespace}) -> {filename}'.format(
            namespace=self.namespace, filename=self.filename)

    def handle_generate_metrics_report(self, message):
        namespace = self._get_namespace()
        self.writer.write(namespace)

    def _get_namespace(self):
        return collect_metrics(self.messagebus, self.namespace)
