import functools
import itertools
import logging

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, FrameworkExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from metrics import GENERATE_METRICS_AGGREGATE
from metrics.metrics import FlatMetricsNamespaceDataView

from . import SERIES_AGGREGATOR_IDS, SERIES_AGGREGATOR_TYPE, SOURCE_SERIES, TARGET_VALUE
from ..messages import collect_metrics

logger = logging.getLogger(get_logger_name('k2', 'metrics', 'aggregators', 'series'))
logger.addHandler(logging.NullHandler())


@FrameworkExtension(
    name='metrics',
    config_options=[
        ConfigOption(SERIES_AGGREGATOR_IDS, required=False, instantiate_on=True),
        ConfigOption(SOURCE_SERIES, required=True),
        ConfigOption(TARGET_VALUE, required=True),
        ConfigOption(SERIES_AGGREGATOR_TYPE, required=True),
    ],
    groups=['metrics'],
)
class MetricsSeriesAggregator(AbstractExtension):
    """
    Evaluate a series of metrics and produce an aggregated result.

    The aggregated result can be:
    * The minimum value of the series
    * The maximum value of the series
    * The average value of the series

    The resulting value is stored as a single value metric.
    If no aggregate can be produced, no result is stored.
    """

    def __init__(self, config, instances):
        self._entity = config.get(SERIES_AGGREGATOR_IDS)
        self._source_series = config.get(SOURCE_SERIES)
        self._target_value = config.get(TARGET_VALUE)
        self._type = config.get(SERIES_AGGREGATOR_TYPE)

    @callback_dispatcher([GENERATE_METRICS_AGGREGATE], optional=True)
    @requires(messagebus='MessageBus')
    @requires(create_single_value_metric='CreateSingleValueMetric')
    def handle_generate_metrics_report(self, message, messagebus, create_single_value_metric):
        for series in self._source_series:
            values = FlatMetricsNamespaceDataView(self._get_namespace(messagebus,
                                                                      series)).get_data().values()
        operator = {
            'min': functools.partial(self._aggregate, min),
            'max': functools.partial(self._aggregate, max),
            'average': functools.partial(self._aggregate, lambda seq: sum(seq) / len(seq))
        }[self._type]
        value = operator(values)
        if value:
            create_single_value_metric(self._target_value, value)

    def _aggregate(self, operator, seqs):
        try:
            return operator(list(itertools.chain.from_iterable(seqs)))
        except ValueError:
            msg = 'Could not aggregate series: {series}'.format(series=self._source_series)
            logger.debug(msg, exc_info=True)
            logger.error(msg)

    def _get_namespace(self, messagebus, series):
        return collect_metrics(messagebus, series)
