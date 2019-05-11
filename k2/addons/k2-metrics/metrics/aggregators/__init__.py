from zaf.config.options import ConfigOptionId
from zaf.config.types import Choice

SERIES_AGGREGATOR_IDS = ConfigOptionId(
    name='ids',
    description='Names a series value aggregator instance',
    multiple=True,
    entity=True,
    namespace='metrics.aggregators.series',
)

SOURCE_SERIES = ConfigOptionId(
    name='source.namespace',
    description='The metrics series to aggregate the values of',
    multiple=True,
    at=SERIES_AGGREGATOR_IDS,
)

TARGET_VALUE = ConfigOptionId(
    name='target.namespace',
    description='The metrics namespace to write the results to',
    at=SERIES_AGGREGATOR_IDS,
)

SERIES_AGGREGATOR_TYPE = ConfigOptionId(
    name='type',
    description='Type of aggregator',
    option_type=Choice(['min', 'max', 'average']),
    at=SERIES_AGGREGATOR_IDS,
)
