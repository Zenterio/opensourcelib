from zaf.config.options import ConfigOptionId
from zaf.config.types import ConfigChoice
from zaf.messages.message import MessageId

from k2.sut import SUT

K2_UPGRADE_COMPONENT = 'Upgrader'
UPGRADE_DEFAULT_TIMEOUT = 1800

AVAILABLE_UPGRADE_TYPES = ConfigOptionId(
    'upgrade.available', 'A collection of all available upgrade types', multiple=True)

UPGRADE_TYPE = ConfigOptionId(
    'upgrade.type',
    'The type of upgrade.',
    at=SUT,
    option_type=ConfigChoice(AVAILABLE_UPGRADE_TYPES))

PERFORM_UPGRADE = MessageId(
    'PERFORM_UPGRADE', """\
    Perform a full software upgrade.

    exception if something failed.
    """)
