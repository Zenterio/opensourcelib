"""
Upgrade SUT software.

Interface addon for upgrading software on a SUT.
"""

import logging

from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import FrameworkExtension, get_logger_name
from zaf.utils.future import FuturesCollection

from k2.sut import SUT
from upgrade.upgrader import Upgrader

logger = logging.getLogger(get_logger_name('k2', 'upgrade'))


def upgrade(core):
    """Upgrades SUTs with the given software."""
    software = core.config.get(UPGRADE_SOURCE)
    suts = core.config.get(SUT)

    error_occurred = False
    future_sut = dict()
    for sut in suts:
        try:
            upgrader = Upgrader(core.messagebus, sut, None)
            future = upgrader.start_upgrade(software)
            future_sut[future] = sut
        except Exception:
            msg = 'Error starting upgrade for sut {sut}'.format(sut=sut)
            logger.debug(msg, exc_info=True)
            logger.warning(msg)
            error_occurred = True
            pass

    futures = FuturesCollection(future_sut.keys())
    for future in futures.as_completed():
        exception = future.exception()
        if exception:
            try:
                raise exception
            except Exception as e:
                msg = 'Failed to upgrade sut {sut}: {exception}'.format(
                    sut=future_sut[future], exception=str(e))
                logger.debug(msg, exc_info=True)
                logger.warning(msg)
                error_occurred = True
        else:
            logger.info('Successfully upgraded sut {sut}'.format(sut=future_sut[future]))

    return 1 if error_occurred else 0


UPGRADE_SOURCE = ConfigOptionId(
    'upgrade.source',
    'The software to upgrade to. Usully the path to an upgrade package.',
    option_type=str,
    argument=True)

UPGRADE_COMMAND = CommandId(
    'upgrade',
    upgrade.__doc__,
    upgrade,
    config_options=[ConfigOption(UPGRADE_SOURCE, required=True),
                    ConfigOption(SUT, required=True)],
    uses=['sut'])


@FrameworkExtension(
    name='upgrade',
    commands=[UPGRADE_COMMAND],
    groups=['upgrade'],
)
class UpgradeExtension(object):
    """Provides the upgrade command."""

    def __init__(self, config, instances):
        pass
