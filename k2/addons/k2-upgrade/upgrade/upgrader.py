import logging
from concurrent.futures import TimeoutError

from zaf.extensions.extension import get_logger_name

from upgrade import PERFORM_UPGRADE, UPGRADE_DEFAULT_TIMEOUT

logger = logging.getLogger(get_logger_name('k2', 'upgrade'))


class NoUpgradeTypes(Exception):
    pass


class MultipleUpgradeTypes(Exception):
    pass


class UpgradeFailed(Exception):
    pass


class Upgrader(object):

    def __init__(self, messagebus, entity, receiver_endpoint_id):
        self.messagebus = messagebus
        self.entity = entity
        self.receiver_endpoint_id = receiver_endpoint_id

    def _singular_future_or_raise(self, futures):
        if len(futures) == 0:
            msg = 'Upgrade failed due to no upgrade types available for sut {sut}'.format(
                sut=self.entity)
            logger.error(msg)
            raise NoUpgradeTypes(msg)
        elif len(futures) > 1:
            msg = 'Upgrade failed due to multiple upgrade types registered for sut {sut}'.format(
                sut=self.entity)
            logger.error(msg)
            raise MultipleUpgradeTypes(msg)

    def start_upgrade(self, software):
        logger.info('Upgrading sut {sut}'.format(sut=self.entity))
        futures = self.messagebus.send_request(
            PERFORM_UPGRADE,
            receiver_endpoint_id=self.receiver_endpoint_id,
            entity=self.entity,
            data=software)
        self._singular_future_or_raise(futures)
        return futures[0]

    def perform_upgrade(self, software):
        """Perform software upgrade."""
        try:
            return self.start_upgrade(software).wait(timeout=UPGRADE_DEFAULT_TIMEOUT)
        except TimeoutError:
            msg = 'Timeout while waiting for sut {sut} to upgrade "{sw}"'.format(
                sut=self.entity, sw=software)
            logger.error(msg)
            raise UpgradeFailed(msg) from None
