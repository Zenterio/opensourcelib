"""
A :ref:`connection check <extension-connectioncheck>` implementation for power switches.

This is a general implementation that uses the currently configured power switch
and because of that there is no need to implement specific connection checks for different
power switches.
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

from . import POWER_SWITCH, POWER_SWITCH_CONNECTION_CHECK_ENABLED, \
    POWER_SWITCH_CONNECTION_CHECK_ENDPOINT, POWER_SWITCH_CONNECTION_CHECK_REQUIRED
from .powerswitch import PowerSwitch

logger = logging.getLogger(get_logger_name('k2', 'powerswitchcc'))


@CommandExtension(
    name='powerswitchcc',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(POWER_SWITCH, required=False),
        ConfigOption(POWER_SWITCH_CONNECTION_CHECK_ENABLED, required=True),
        ConfigOption(POWER_SWITCH_CONNECTION_CHECK_REQUIRED, required=True),
    ],
    endpoints_and_messages={POWER_SWITCH_CONNECTION_CHECK_ENDPOINT: [
        CONNECTIONCHECK_RUN_CHECK,
    ]},
    groups=['connectioncheck', 'powerswitch'],
    activate_on=[POWER_SWITCH, POWER_SWITCH_CONNECTION_CHECK_ENABLED])
class PowerSwitchConnectionCheck(AbstractExtension):
    """
    Powerswitch connection check.

    Checks that it's possible to connect to the power switch for the SUT.
    """

    def __init__(self, config, instances):
        self._required = config.get(POWER_SWITCH_CONNECTION_CHECK_REQUIRED)
        self._entity = instances.get(SUT)

    @callback_dispatcher(
        [CONNECTIONCHECK_RUN_CHECK], [POWER_SWITCH_CONNECTION_CHECK_ENDPOINT], entity_option_id=SUT)
    @requires(messagebus='MessageBus')
    def run_check(self, message, messagebus):
        logger.info(
            'Running powerswitch connection check for entity {entity}'.format(entity=self._entity))

        client = PowerSwitch(messagebus, self._entity, receiver_endpoint_id=None)
        try:
            client.state()
            logger.info(
                'Powerswitch connection check for entity {entity} was successful'.format(
                    entity=self._entity))
            return ConnectionCheckResult(
                self.name, success=True, required=self._required, message='')
        except Exception as e:
            logger.debug('Powerswitch connection check failed', exc_info=True)
            return ConnectionCheckResult(
                self.name,
                success=False,
                required=self._required,
                message='Powerswitch connection check failed: {error}'.format(error=str(e)))
