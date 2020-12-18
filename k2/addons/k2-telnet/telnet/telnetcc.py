"""
A :ref:`connection check <extension-connectioncheck>` implementation for telnet.

Checks that the telnet connection is working by trying to connect and send a command.
"""

import logging

from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from connectioncheck import CONNECTIONCHECK_RUN_CHECK
from connectioncheck.connectioncheck import ConnectionCheckResult
from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT, SUT_IP

from . import TELNET_CONNECTION_CHECK_ENABLED, TELNET_CONNECTION_CHECK_ENDPOINT, \
    TELNET_CONNECTION_CHECK_REQUIRED, TELNET_ENABLED, TELNET_PORT
from .client import TelnetClient

logger = logging.getLogger(get_logger_name('k2', 'telnetcc'))


@CommandExtension(
    name='telnetcc',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(SUT_IP, required=True),
        ConfigOption(TELNET_ENABLED, required=True),
        ConfigOption(TELNET_CONNECTION_CHECK_ENABLED, required=True),
        ConfigOption(TELNET_CONNECTION_CHECK_REQUIRED, required=True),
        ConfigOption(TELNET_PORT, required=True),
    ],
    endpoints_and_messages={TELNET_CONNECTION_CHECK_ENDPOINT: [
        CONNECTIONCHECK_RUN_CHECK,
    ]},
    groups=['connectioncheck', 'telnet'],
    activate_on=[TELNET_ENABLED, TELNET_CONNECTION_CHECK_ENABLED])
class TelnetConnectionCheck(AbstractExtension):
    """Telnet connection check."""

    def __init__(self, config, instances):
        self._required = config.get(TELNET_CONNECTION_CHECK_REQUIRED)
        self._entity = instances.get(SUT)

        self._ip = config.get(SUT_IP)
        self._port = config.get(TELNET_PORT)

    @callback_dispatcher(
        [CONNECTIONCHECK_RUN_CHECK], [TELNET_CONNECTION_CHECK_ENDPOINT], entity_option_id=SUT)
    def run_check(self, message):
        logger.info(
            'Running telnet connection check towards {ip}:{port}'.format(
                ip=self._ip, port=self._port))

        try:
            with TelnetClient(self._ip, self._port) as client:
                client.send_line('true', expected_exit_code=0)
                logger.info(
                    'Telnet connection check for sut {entity} was successful'.format(
                        entity=self._entity))
            return ConnectionCheckResult(
                self.name, success=True, required=self._required, message='')
        except Exception as e:
            logger.debug('Telnet connection check failed', exc_info=True)
            return ConnectionCheckResult(
                self.name,
                success=False,
                required=self._required,
                message='Telnet connection check failed: {error}'.format(error=str(e)))
