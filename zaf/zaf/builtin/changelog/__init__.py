from enum import Enum, unique
from zaf.config.options import ConfigOptionId


@unique
class ChangeLogType(Enum):

    # Use internal generated in a Znake compatible format
    ZNAKE = 0

    # Use configureable changelog
    CONFIGURABLE = 1

    # No changelog support
    NONE = 2


CHANGELOG_VERSION = ConfigOptionId(
    'versions',
    'Versions in the changelog. These are entities that can be configured.',
    entity=True,
    multiple=True,
    namespace='changelog',
    hidden=True,
)

CHANGELOG_DATE = ConfigOptionId(
    'date',
    'The date of the change. Needs to be specified in deb compatible format, '
    "for example 'Tue, 11 Dec 2018 17:29:00 +0200'",
    at=CHANGELOG_VERSION,
    hidden=True,
)

CHANGELOG_CHANGES = ConfigOptionId(
    'changes',
    'Description of the changes in this version',
    at=CHANGELOG_VERSION,
    multiple=True,
    hidden=True,
)
