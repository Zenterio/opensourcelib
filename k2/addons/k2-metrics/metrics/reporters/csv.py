import logging
import os

from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import FrameworkExtension, get_logger_name

from k2.utils.writers import CsvWriter

from ..messages import collect_metrics
from ..metrics import FlatMetricsNamespaceDataView
from .reporter import AbstractMetricsReportExtension

logger = logging.getLogger(get_logger_name('k2', 'metrics', 'csv'))
logger.addHandler(logging.NullHandler())

CSV_REPORTER_ID = ConfigOptionId(
    name='ids',
    description='Names a CSV metrics reporter instance',
    multiple=True,
    entity=True,
    namespace='metrics.csv',
)

CSV_DIRECTORY = ConfigOptionId(
    name='dir',
    description='Directory to write the CSV reports to',
    default='${output.dir}/metrics/csv',
    at=CSV_REPORTER_ID,
)

CSV_FILENAME = ConfigOptionId(
    name='filename',
    description='Name of the CSV file to write',
    at=CSV_REPORTER_ID,
)

CSV_NAMESPACE = ConfigOptionId(
    name='namespace',
    description='The metrics namespace to report',
    at=CSV_REPORTER_ID,
)

CSV_METRICS = ConfigOptionId(
    name='metrics',
    description=(
        'Only include metrics that includes this string in its name. '
        'By default, all metrics are included.'),
    at=CSV_REPORTER_ID,
    multiple=True,
)

CSV_RENAME_FROM = ConfigOptionId(
    name='rename.from',
    description=(
        'Used to rename a metric in the CSV '
        'This is a regex that can include match groups that can be used in the to expression'),
    at=CSV_REPORTER_ID,
)

CSV_RENAME_TO = ConfigOptionId(
    name='rename.to',
    description=(
        'Used to rename a metric in the CSV '
        'Default is empty which means to remove the part that matches the from expression'),
    at=CSV_REPORTER_ID,
    default='')


@FrameworkExtension(
    name='metrics',
    config_options=[
        ConfigOption(CSV_REPORTER_ID, required=False, instantiate_on=True),
        ConfigOption(CSV_DIRECTORY, required=True),
        ConfigOption(CSV_FILENAME, required=True),
        ConfigOption(CSV_NAMESPACE, required=True),
        ConfigOption(CSV_METRICS, required=False),
        ConfigOption(CSV_RENAME_FROM, required=False),
        ConfigOption(CSV_RENAME_TO, required=False),
    ],
    groups=['metrics'],
)
class MetricsCsvReporter(AbstractMetricsReportExtension):
    """
    Metrics reporter that writes CSV formatted reports.

    Example report:

    .. code-block:: none

        system_information.cpu_count,system_information.decoder_count
        3,2

    """

    def __init__(self, config, instances):
        super().__init__(config, instances)
        self.filename = config.get(CSV_FILENAME)
        self.writer = CsvWriter(os.path.join(config.get(CSV_DIRECTORY), self.filename))
        self.namespace = config.get(CSV_NAMESPACE)
        self.metrics = config.get(CSV_METRICS)
        self.rename_regex = self.parse_regex_option(config, CSV_RENAME_FROM)
        self.rename_to = config.get(CSV_RENAME_TO)

    def __str__(self):
        return 'MetricsCsvReporter({namespace}) -> {filename}'.format(
            namespace=self.namespace, filename=self.filename)

    def handle_generate_metrics_report(self, message):
        namespace = FlatMetricsNamespaceDataView(
            self._get_namespace(),
            key_filter=self._filter_namespace,
            rename_regex=self.rename_regex,
            rename_to=self.rename_to)
        self.writer.write(namespace)

    def _filter_namespace(self, key):
        return not self.metrics or any(metric in key for metric in self.metrics)

    def _get_namespace(self):
        return collect_metrics(self.messagebus, self.namespace)
