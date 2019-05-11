import logging
from time import sleep

from zaf.extensions.extension import get_logger_name

from powermeter import POWER_METER_POWER, POWER_METER_TIMEOUT

logger = logging.getLogger(get_logger_name('k2', 'powermeter'))


class NoPowerMeter(Exception):
    pass


class MultiplePowerMeters(Exception):
    pass


class PowerMeter(object):

    def __init__(self, messagebus, entity, receiver_endpoint_id):
        self.messagebus = messagebus
        self.entity = entity
        self.receiver_endpoint_id = receiver_endpoint_id

    def _return_or_raise(self, futures, message):
        if len(futures) == 0:
            msg = 'Trying to use powermeter failed due to no powermeter available for sut {entity}'.format(
                entity=self.entity)
            logger.warning(msg)
            raise NoPowerMeter(msg)
        elif len(futures) > 1:
            msg = 'Trying to use powermeter failed due to multiple power meters registered for sut {entity}'.format(
                entity=self.entity)
            logger.warning(msg)
            raise MultiplePowerMeters(msg)
        else:
            return futures[0].result(timeout=0)

    def power(self, num_samples=1, interval=0):
        """
        Return the average power as watts.

        :param num_samples: Number of samples to measure.
        :param interval: Number of seconds to wait between each sample.
        """
        logger.info(
            'Using powermeter to get power consumption for sut {entity}'.format(entity=self.entity))

        logger.debug(
            'Taking {num_samples} sample(s) for power consumption'.format(num_samples=num_samples))
        samples = [0] * num_samples
        for n in range(num_samples):
            futures = self.messagebus.send_request(
                POWER_METER_POWER, self.receiver_endpoint_id,
                self.entity).wait(timeout=POWER_METER_TIMEOUT)
            samples[n] = self._return_or_raise(futures, POWER_METER_POWER)
            logger.debug('Sample #{n}: {power:.2f} W'.format(n=n, power=samples[n]))
            if interval and n < (num_samples - 1):
                sleep(interval)

        power = sum(samples) / len(samples)
        logger.info(
            'Average power consumption for sut {entity} is {power:.2f} W'.format(
                entity=self.entity, power=power))
        return power
