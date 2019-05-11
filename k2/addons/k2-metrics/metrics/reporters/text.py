import logging
import os
import sys

from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import FrameworkExtension, get_logger_name

from ..messages import collect_metrics
from ..metrics import FlatMetricsNamespaceDataView
from .reporter import AbstractMetricsReportExtension

logger = logging.getLogger(get_logger_name('k2', 'metrics', 'text'))
logger.addHandler(logging.NullHandler())

TEXT_REPORTER_ID = ConfigOptionId(
    name='ids',
    description='Names a text metrics reporter instance',
    multiple=True,
    entity=True,
    namespace='metrics.text',
)

TEXT_DIRECTORY = ConfigOptionId(
    name='dir',
    description='Directory to write the Text reports to',
    default='${output.dir}/metrics/text',
    at=TEXT_REPORTER_ID,
)

TEXT_FILENAME = ConfigOptionId(
    name='filename',
    description='Name of the text file to write. If not given the report will be written to stdout',
    at=TEXT_REPORTER_ID)

TEXT_NAMESPACE = ConfigOptionId(
    name='namespace',
    description='The metrics namespace to report',
    at=TEXT_REPORTER_ID,
)

TEXT_METRICS = ConfigOptionId(
    name='metrics',
    description=(
        'Only include metrics that includes this string in its name. '
        'By default, all metrics are included.'),
    at=TEXT_REPORTER_ID,
    multiple=True,
)

TEXT_RENAME_FROM = ConfigOptionId(
    name='rename.from',
    description=(
        'Used to rename a metric in the report '
        'This is a regex that can include match groups that can be used in the to expression'),
    at=TEXT_REPORTER_ID,
)

TEXT_RENAME_TO = ConfigOptionId(
    name='rename.to',
    description=(
        'Used to rename a metric in the report '
        'Default is empty which means to remove the part that matches the from expression'),
    at=TEXT_REPORTER_ID,
    default='')


@FrameworkExtension(
    name='metrics',
    config_options=[
        ConfigOption(TEXT_REPORTER_ID, required=False, instantiate_on=True),
        ConfigOption(TEXT_DIRECTORY, required=True),
        ConfigOption(TEXT_FILENAME, required=False),
        ConfigOption(TEXT_NAMESPACE, required=True),
        ConfigOption(TEXT_METRICS, required=False),
        ConfigOption(TEXT_RENAME_FROM, required=False),
        ConfigOption(TEXT_RENAME_TO, required=False),
    ],
    groups=['metrics'],
)
class MetricsTextReporter(AbstractMetricsReportExtension):
    """
    Metrics reporter that writes human readable text formatted report.

    Example report:

    .. code-block:: none

        system_information.cpu_count: 3
        system_information.decoder_count: 2

    """

    def __init__(self, config, instances):
        super().__init__(config, instances)
        self.file_name = config.get(TEXT_FILENAME)
        self.dir = config.get(TEXT_DIRECTORY)
        self.namespace = config.get(TEXT_NAMESPACE)
        self.metrics = config.get(TEXT_METRICS)
        self.rename_regex = self.parse_regex_option(config, TEXT_RENAME_FROM)
        self.rename_to = config.get(TEXT_RENAME_TO)

    def __str__(self):
        return 'MetricsTextReporter({namespace}) -> {filename}'.format(
            namespace=self.namespace,
            filename=self.file_name if self.file_name is not None else 'stdout')

    def handle_generate_metrics_report(self, message):
        namespace = FlatMetricsNamespaceDataView(
            self._get_namespace(),
            key_filter=self._filter_namespace,
            rename_regex=self.rename_regex,
            rename_to=self.rename_to)
        if self.file_name is not None:
            os.makedirs(self.dir, exist_ok=True)
            with open(os.path.join(self.dir, self.file_name), 'w') as f:
                self._write_report(namespace.get_data(), f)
        else:
            self._write_report(namespace.get_data(), sys.stdout)

    def _write_report(self, data, output_stream):
        for k, v in data.items():
            output_stream.write('{key}: {value}\n'.format(key=k, value=v))

    def _filter_namespace(self, key):
        return not self.metrics or any(metric in key for metric in self.metrics)

    def _get_namespace(self):
        return collect_metrics(self.messagebus, self.namespace)
