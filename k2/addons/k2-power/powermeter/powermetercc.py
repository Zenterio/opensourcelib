"""
A :ref:`connection check <extension-connectioncheck>` implementation for power meters.

This is a general implementation that uses the currently configured power meter
and because of that there is no need to implement specific connection checks for different
power meters.
"""
import logging

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from connectioncheck import CONNECTIONCHECK_RUN_CHECK
from connectioncheck.connectioncheck import ConnectionCheckResult
from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT

from . import POWER_METER, POWER_METER_CONNECTION_CHECK_ENABLED, \
    POWER_METER_CONNECTION_CHECK_ENDPOINT, POWER_METER_CONNECTION_CHECK_REQUIRED
from .powermeter import PowerMeter

logger = logging.getLogger(get_logger_name('k2', 'powermetercc'))


@CommandExtension(
    name='powermetercc',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(POWER_METER, required=False),
        ConfigOption(POWER_METER_CONNECTION_CHECK_ENABLED, required=True),
        ConfigOption(POWER_METER_CONNECTION_CHECK_REQUIRED, required=True),
    ],
    endpoints_and_messages={POWER_METER_CONNECTION_CHECK_ENDPOINT: [
        CONNECTIONCHECK_RUN_CHECK,
    ]},
    groups=['connectioncheck', 'powermeter'],
    activate_on=[POWER_METER, POWER_METER_CONNECTION_CHECK_ENABLED])
class PowerMeterConnectionCheck(AbstractExtension):
    """
    Power meter connection check.

    Checks that it's possible to connect to the power meter for the SUT.
    """

    def __init__(self, config, instances):
        self._required = config.get(POWER_METER_CONNECTION_CHECK_REQUIRED)
        self._entity = instances.get(SUT)

    @callback_dispatcher(
        [CONNECTIONCHECK_RUN_CHECK], [POWER_METER_CONNECTION_CHECK_ENDPOINT], entity_option_id=SUT)
    @requires(messagebus='MessageBus')
    def run_check(self, message, messagebus):
        logger.info(
            'Running power meter connection check for entity {entity}'.format(entity=self._entity))

        client = PowerMeter(messagebus, self._entity, receiver_endpoint_id=None)
        try:
            client.power()
            logger.info(
                'Power meter connection check for entity {entity} was successful'.format(
                    entity=self._entity))
            return ConnectionCheckResult(
                self.name, success=True, required=self._required, message='')
        except Exception as e:
            logger.debug('Power meter connection check failed', exc_info=True)
            return ConnectionCheckResult(
                self.name,
                success=False,
                required=self._required,
                message='Power meter connection check failed: {error}'.format(error=str(e)))
