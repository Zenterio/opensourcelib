"""
Provides serial connection support.

The usage of the connection is handled over messages SERIAL_SEND_COMMAND and LOG_LINE_RECEIVED.
The SERIAL_SEND_COMMAND message data should be a string representing a line to send on the serial connection.
For each line read from the serial connection a LOG_LINE_RECEIVED will be sent.

To communicate with the correct instance of the serial connection the SUT
instance should be used as the messagebus entity.

It's also possible to use the serial connection using the component that
implements the :ref:`exec <exec-label>` interface.
"""

import logging
import time

from zaf.application import APPLICATION_ENDPOINT, BEFORE_COMMAND
from zaf.component.decorator import component, requires
from zaf.component.util import add_cans, add_properties
from zaf.config import MissingConditionalConfigOption
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher, sequential_dispatcher

from k2 import CRITICAL_EXTENSION_ERROR
from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT
from sutevents import LOG_LINE_RECEIVED
from zserial import SERIAL_RAW_LINE, SERIAL_RECONNECT

from . import SERIAL_BAUDRATE, SERIAL_CONNECTED, SERIAL_CONNECTION_LOST, SERIAL_DEVICE, \
    SERIAL_ENABLED, SERIAL_ENDPOINT, SERIAL_FILTERS, SERIAL_PROMPT, SERIAL_SEND_COMMAND, \
    SERIAL_TIMEOUT
from .client import SerialClient
from .connection import find_serial_port, start_serial_connection
from .messages import SendSerialCommandData

logger = logging.getLogger(get_logger_name('k2', 'zserial'))

NUMBER_OF_RECONNECTION_TRIES = 30
TIMEOUT_BETWEEN_CONNECTIONS = 1


class SerialException(Exception):
    pass


@requires(sut='Sut', can=['serial'])
@requires(messagebus='MessageBus')
@component(name='Exec', can=['serial'], provided_by_extension='zserial', priority=-1)
def serial_exec(sut, messagebus):
    """Exec component using serial."""
    return SerialClient(messagebus, sut.entity, sut.serial.timeout, sut.serial.prompt)


@CommandExtension(
    name='zserial',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(SERIAL_ENABLED, required=True),
        ConfigOption(SERIAL_DEVICE, required=False),
        ConfigOption(SERIAL_BAUDRATE, required=False),
        ConfigOption(SERIAL_PROMPT, required=False),
        ConfigOption(SERIAL_FILTERS, required=False),
        ConfigOption(SERIAL_TIMEOUT, required=False)
    ],
    endpoints_and_messages={
        SERIAL_ENDPOINT: [
            SERIAL_SEND_COMMAND, LOG_LINE_RECEIVED, SERIAL_CONNECTION_LOST, SERIAL_CONNECTED,
            CRITICAL_EXTENSION_ERROR, SERIAL_RECONNECT, SERIAL_RAW_LINE
        ]
    },
    groups=['exec', 'serial'],
    activate_on=[SERIAL_ENABLED],
)
class SerialExtension(AbstractExtension):
    """Serial connection."""

    def __init__(self, config, instances):
        self._enabled = config.get(SERIAL_ENABLED)
        self._active = False
        self._entity = instances.get(SUT)

        self._port = None
        self._virtual = None
        self._serial_connection = None

        self._baudrate = config.get(SERIAL_BAUDRATE)
        self._prompt = config.get(SERIAL_PROMPT)
        self._timeout = config.get(SERIAL_TIMEOUT)
        self._filters = config.get(SERIAL_FILTERS)

        if self._enabled is True:
            device = config.get(SERIAL_DEVICE)
            if device is None:
                msg = 'Missing serial connection device'
                raise MissingConditionalConfigOption(msg)

            self._port, self._virtual = find_serial_port(device)

    def register_components(self, component_manager):
        if self._enabled:
            sut = component_manager.get_unique_class_for_entity(self._entity)
            add_cans(sut, ['serial'])
            add_properties(sut, 'serial', {
                'prompt': self._prompt,
                'timeout': self._timeout,
            })

    @callback_dispatcher([BEFORE_COMMAND], [APPLICATION_ENDPOINT])
    @requires(messagebus='MessageBus')
    def before_command(self, message, messagebus):
        self._active = True
        self.open_serial_port(messagebus)

    @sequential_dispatcher([SERIAL_SEND_COMMAND], [SERIAL_ENDPOINT], entity_option_id=SUT)
    def send_serial_command(self, message):
        data = message.data
        if isinstance(message.data, SendSerialCommandData):
            self._send_serial_command(data.line, event=data.event, timeout=data.timeout)
        else:
            self._send_serial_command(data)

    def _send_serial_command(self, line, event=None, timeout=None):
        if self._serial_connection is None:
            raise SerialException(
                (
                    'Error when trying to send serial command \'{line}\'. '
                    'Serial connection closed').format(line=line))
        self._serial_connection.write_line(line)
        if event is not None:
            event.wait(timeout)

    @sequential_dispatcher([SERIAL_RAW_LINE], [SERIAL_ENDPOINT], entity_option_id=SUT)
    def handle_raw_line(self, message):
        raw_line = message.data
        self._serial_connection.parse_raw_line(raw_line)

    @sequential_dispatcher(
        [SERIAL_CONNECTION_LOST, SERIAL_RECONNECT], [SERIAL_ENDPOINT], entity_option_id=SUT)
    @requires(messagebus='MessageBus')
    def connection_lost_or_reconnect(self, message, messagebus):
        logger.debug(
            'Received {message}. Reconnecting serial connection'.format(
                message=message.message_id.name))

        self.close_serial_port()
        self.open_serial_port(messagebus)

    def open_serial_port(self, messagebus):
        for i in range(0, NUMBER_OF_RECONNECTION_TRIES):
            if not self._active:
                return

            try:
                self._serial_connection = start_serial_connection(
                    self._port, self._baudrate, self._virtual, self._timeout, messagebus,
                    self._entity, self._filters)
                return
            except Exception:
                logger.debug(
                    'Failed to connect to serial {port}'.format(port=self._port), exc_info=True)
                time.sleep(TIMEOUT_BETWEEN_CONNECTIONS)

        messagebus.trigger_event(CRITICAL_EXTENSION_ERROR, SERIAL_ENDPOINT, self._entity)

    def destroy(self):
        self.close_serial_port()

    def close_serial_port(self):
        if self._serial_connection:
            self._serial_connection.close()
            self._serial_connection = None