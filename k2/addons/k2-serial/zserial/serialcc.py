"""
A :ref:`connection check <extension-connectioncheck>` implementation for serial.

Checks that the serial connection is working by trying to connect and send a command.
"""
import grp
import logging
import os

from zaf.component.decorator import requires
from zaf.config import MissingConditionalConfigOption
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.dispatchers import CallbackDispatcher

from connectioncheck import CONNECTIONCHECK_RUN_CHECK
from connectioncheck.connectioncheck import ConnectionCheckResult
from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT
from zserial import SERIAL_ENDPOINT, SERIAL_PORT_IDS, SERIAL_RECONNECT

from . import SERIAL_CONNECTION_CHECK_ENABLED, SERIAL_CONNECTION_CHECK_ENDPOINT, \
    SERIAL_CONNECTION_CHECK_REQUIRED, SERIAL_ENABLED, SERIAL_TIMEOUT, SUT_SERIAL_PORTS
from .client import SerialClient
from .sut import SUT_SERIAL_CONNECTION_CHECK_ENABLED, SUT_SERIAL_CONNECTION_CHECK_REQUIRED

logger = logging.getLogger(get_logger_name('k2', 'zserialcc'))


@CommandExtension(
    name='zserialcc',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SERIAL_PORT_IDS, required=True, instantiate_on=True),
        ConfigOption(SERIAL_ENABLED, required=True),
        ConfigOption(SERIAL_CONNECTION_CHECK_ENABLED, required=True),
        ConfigOption(SERIAL_CONNECTION_CHECK_REQUIRED, required=True),
        ConfigOption(SERIAL_TIMEOUT, required=True),
        ConfigOption(SUT, required=True),
        ConfigOption(SUT_SERIAL_PORTS, required=True),
        ConfigOption(SUT_SERIAL_CONNECTION_CHECK_ENABLED, required=False),
        ConfigOption(SUT_SERIAL_CONNECTION_CHECK_REQUIRED, required=False),
    ],
    endpoints_and_messages={SERIAL_CONNECTION_CHECK_ENDPOINT: [
        CONNECTIONCHECK_RUN_CHECK,
    ]},
    groups=['connectioncheck', 'serial'],
    activate_on=[SERIAL_ENABLED, SERIAL_CONNECTION_CHECK_ENABLED],
)
class SerialConnectionCheck(AbstractExtension):
    """Serial connection check."""

    def __init__(self, config, instances):
        self._enabled = config.get(SERIAL_ENABLED) and config.get(SERIAL_CONNECTION_CHECK_ENABLED)
        self._required = config.get(SERIAL_CONNECTION_CHECK_REQUIRED)
        self._entity = instances.get(SERIAL_PORT_IDS)
        self._timeout = config.get(SERIAL_TIMEOUT)

        self._suts = [
            sut for sut in config.get(SUT)
            if self._entity in config.get(SUT_SERIAL_PORTS, entity=sut)
        ]

        if self._enabled and not self._suts:
            msg = "Error: connection check enabled for '{port}' but no suts who listens".format(
                port=self._entity)
            raise MissingConditionalConfigOption(msg)

    def register_dispatchers(self, messagebus):
        if self._enabled:
            self.dispatcher = CallbackDispatcher(messagebus, self.run_check)
            self.dispatcher.register(
                [CONNECTIONCHECK_RUN_CHECK], [SERIAL_CONNECTION_CHECK_ENDPOINT],
                entities=self._suts)

    @requires(messagebus='MessageBus')
    def run_check(self, message, messagebus):
        logger.info(
            'Running serial connection check for entity {entity}'.format(entity=self._entity))

        client = SerialClient(messagebus, self._entity, timeout=self._timeout)

        result = self._perform_check(client)
        if result.success:
            return result

        try:
            logger.debug(
                'Trigger reconnect of serial connection for entity {entity}.'.format(
                    entity=self._entity))
            messagebus.send_request(
                SERIAL_RECONNECT, SERIAL_ENDPOINT,
                entity=self._entity).wait(self._timeout)[0].result()
        except Exception as e:
            logger.debug(
                'Reconnect of serial connection failed for entity {entity}.'.format(
                    entity=self._entity),
                exc_info=True)

            return ConnectionCheckResult(
                self.name,
                success=False,
                required=self._required,
                message='Serial connection check failed to reconnect serial connection: {error}'.
                format(error=str(e)))

        return self._perform_check(client)

    def _perform_check(self, client):
        try:
            client.send_line('echo test')
            logger.info(
                'Serial connection check for port {entity} was successful'.format(
                    entity=self._entity))
            return ConnectionCheckResult(
                self.name, success=True, required=self._required, message='')

        except Exception as e:
            self._check_if_member_of_dialout_group()
            msg = 'Serial connection check failed for {entity}: {error}'.format(
                entity=self._entity, error=str(e))
            logger.debug(msg, exc_info=True)
            return ConnectionCheckResult(
                self.name, success=False, required=self._required, message=msg)

    def _check_if_member_of_dialout_group(self):
        try:
            dialout_gid = grp.getgrnam('dialout').gr_gid
        except KeyError:
            # The dialout group does not exist.
            # Do nothing, as we are most likely not running on a Debian style system.
            return
        if dialout_gid not in os.getgroups():
            msg = (
                'The user running this K2 process is not a member of the "dialout" group. '
                'This will most likely lead to the serial port being inaccessible. '
                'Make sure to add the current user to the "dialout" group to remedy this issue.')
            logger.warning(msg)
