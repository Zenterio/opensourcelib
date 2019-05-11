from zaf.config.options import ConfigOptionId
from zaf.config.types import Count

VERBOSE = ConfigOptionId(
    'verbose',
    'Increase output verbosity. Can be provided multiple times e.g. -vvv.',
    option_type=Count(0, 1),
    short_name='v',
    default=0,
)
