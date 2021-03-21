import logging
import time

from zaf.component.decorator import component, requires
from zaf.extensions.extension import get_logger_name

from powerswitch import POWER_SWITCH_POWER_STATE, POWER_SWITCH_POWEROFF, POWER_SWITCH_POWERON, \
    POWER_SWITCH_TIMEOUT

logger = logging.getLogger(get_logger_name('k2', 'powerswitch'))

POWER_CYCLE_TIME = 30


class NoPowerSwitch(Exception):
    pass


class MultiplePowerSwitches(Exception):
    pass


class PowerSwitch(object):

    def __init__(self, messagebus, entity, receiver_endpoint_id):
        self.messagebus = messagebus
        self.entity = entity
        self.receiver_endpoint_id = receiver_endpoint_id

    def _return_or_raise(self, futures, message):
        if len(futures) == 0:
            msg = 'Trying to use powerswitch failed due to no powerswitch available for sut {entity}'.format(
                entity=self.entity)
            logger.warning(msg)
            raise NoPowerSwitch(msg)
        elif len(futures) > 1:
            msg = 'Trying to use powerswitch failed due to multiple power switchs registered for sut {entity}'.format(
                entity=self.entity)
            logger.warning(msg)
            raise MultiplePowerSwitches(msg)
        else:
            return futures[0].result(timeout=0)

    def on(self):
        """Turn on power."""
        logger.info(
            'Using powerswitch to turn on power for sut {entity}'.format(entity=self.entity))
        futures = self.messagebus.send_request(
            POWER_SWITCH_POWERON, self.receiver_endpoint_id,
            self.entity).wait(timeout=POWER_SWITCH_TIMEOUT)
        return self._return_or_raise(futures, POWER_SWITCH_POWERON)

    def off(self):
        """Turn off power."""
        logger.info(
            'Using powerswitch to turn off power for sut {entity}'.format(entity=self.entity))
        futures = self.messagebus.send_request(
            POWER_SWITCH_POWEROFF, self.receiver_endpoint_id,
            self.entity).wait(timeout=POWER_SWITCH_TIMEOUT)
        return self._return_or_raise(futures, POWER_SWITCH_POWEROFF)

    def state(self):
        """Return the power state as True/False."""
        logger.info(
            'Using powerswitch to get power state for sut {entity}'.format(entity=self.entity))
        futures = self.messagebus.send_request(
            POWER_SWITCH_POWER_STATE, self.receiver_endpoint_id,
            self.entity).wait(timeout=POWER_SWITCH_TIMEOUT)
        state = self._return_or_raise(futures, POWER_SWITCH_POWER_STATE)
        logger.info(
            'Power switch state for sut {entity} is {state}'.format(
                entity=self.entity, state='ON' if state else 'OFF'))
        return state

    def off_then_on(self, off_time=POWER_CYCLE_TIME):
        """
        Toggles the state of the powerswitch first to off and then to on.

        If already off then this only turns on the power.

        :param off_time: number of seconds to wait before turning on.
        """
        logger.info(
            'Using powerswitch to toggle power off then on for sut {entity}'.format(
                entity=self.entity))
        initial_state = self.state()
        if initial_state:
            self.off()

        if off_time:
            logger.info(
                'Waiting {seconds} seconds before turning on power again for sut {entity}'.format(
                    seconds=off_time, entity=self.entity))
            time.sleep(off_time)

        self.on()


@component
@requires(switch='PowerSwitch')
@requires(sutevents='SutEvents')
class SutPowerControl(object):
    """Helper component to control the power to a SUT."""

    def __init__(self, switch, sutevents):
        self._switch = switch
        self._sutevents = sutevents

    def power_cycle_sut(self, off_time=POWER_CYCLE_TIME):
        with self._sutevents.expect_reset():
            with self._sutevents.await_sut_reset_done():
                self._switch.off_then_on(off_time=off_time)
