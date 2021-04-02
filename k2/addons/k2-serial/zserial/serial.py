"""
Provides serial connection support.

The usage of the connection is handled over messages SERIAL_SEND_COMMAND and LOG_LINE_RECEIVED.
The SERIAL_SEND_COMMAND message data should be a string representing a line to send on the serial connection.
For each line read from the serial connection a LOG_LINE_RECEIVED will be sent.

To communicate with the correct instance of the serial connection the SERIAL_PORT_IDS
instance should be used as the messagebus entity.

It's also possible to use the serial connection using the component that
implements the :ref:`exec <exec-label>` interface.
"""

import logging
import time
from contextlib import contextmanager

from zaf.application import APPLICATION_ENDPOINT, BEFORE_COMMAND
from zaf.component.decorator import component, requires
from zaf.component.util import add_properties
from zaf.config import MissingConditionalConfigOption
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, ExtensionConfig, \
    FrameworkExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher, sequential_dispatcher

from k2 import CRITICAL_EXTENSION_ERROR
from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT
from k2.sut.log import sut_add_log_source
from sutevents import LOG_LINE_RECEIVED
from zserial import SERIAL_RAW_LINE, SERIAL_RECONNECT

from . import SERIAL_BAUDRATE, SERIAL_CONNECTED, SERIAL_CONNECTION_LOST, SERIAL_DEVICE, \
    SERIAL_ENABLED, SERIAL_ENDPOINT, SERIAL_FILTERS, SERIAL_LOG_ENABLED, SERIAL_PORT_IDS, \
    SERIAL_PROMPT, SERIAL_RESUME, SERIAL_SEND_COMMAND, SERIAL_SUSPEND, SERIAL_TIMEOUT, \
    SUT_SERIAL_PORTS
from .client import SerialClient
from .connection import find_serial_port, start_serial_connection
from .log import serial_log_line_entity
from .messages import SendSerialCommandData
from .sut import SUT_SERIAL_BAUDRATE, SUT_SERIAL_DEVICE, SUT_SERIAL_ENABLED, SUT_SERIAL_FILTERS, \
    SUT_SERIAL_LOG_ENABLED, SUT_SERIAL_PROMPT, SUT_SERIAL_TIMEOUT, \
    add_sut_options_to_extension_config

logger = logging.getLogger(get_logger_name('k2', 'zserial'))

NUMBER_OF_RECONNECTION_TRIES = 30
TIMEOUT_BETWEEN_CONNECTIONS = 1


class SerialException(Exception):
    pass


@requires(port='SerialPort')
@requires(messagebus='MessageBus')
@component(name='Exec', can=['serial'], provided_by_extension='zserial', priority=-1)
def serial_exec(port, messagebus):
    """Exec component using serial."""
    return SerialClient(messagebus, port.entity, port.serial.timeout, port.serial.prompt)


@requires(port='SerialPort')
@requires(messagebus='MessageBus')
@component(name='RawSerialPort', can=['serial'], provided_by_extension='zserial')
class RawSerialPort(object):
    """
    Access the serial port in raw byte mode.

    Temporarily suspend the packetized log line handling to provide raw byte
    access to the serial port.

    .. warning:: This component is not thread safe. Suspending the same serial port multiple times will break.

    Example:

    .. code-block:: python

        @requires(serial='RawSerialPort')
        @requires(exec='Exec', can=['serial'])
        def test_xmodem_recv(serial,exec):
            with open('/dev/null', 'wb') as f:
                exec.send_line('sz -X --1k -q /proc/cpuinfo',
                    prefix_output=False,
                    endmark='Give your local XMODEM receive command now.')
                with serial.suspended() as ser:
                    def getc(size, timeout=1):
                        return ser.read(size) or None

                    def putc(data, timeout=1):
                        return ser.write(data)

                    modem = XMODEM1k(getc, putc)
                    modem.recv(f)

        @requires(serial='RawSerialPort')
        @requires(exec='Exec', can=['serial'])
        def test_xmodem_send(serial,exec):
            with open('/proc/version', 'rb') as f:
                exec.send_line('rz -X -q -y /dev/null',
                    prefix_output=False,
                    endmark='rz: ready to receive /tmp/foo')
                with serial.suspended() as ser:
                    def getc(size, timeout=1):
                        return ser.read(size) or None

                    def putc(data, timeout=1):
                        return ser.write(data)

                    modem = XMODEM1k(getc, putc)
                    modem.send(f)
    """

    def __init__(self, port, messagebus):
        self._entity = port.entity
        self._messagebus = messagebus

    @contextmanager
    def suspended(self):
        """Temporarily suspend the normal serial log line handling."""

        try:
            yield self.suspend()
        finally:
            self.resume()

    def suspend(self):
        logger.debug('Suspending serial port for entity {entity}'.format(entity=self._entity))
        return self._messagebus.send_request(
            SERIAL_SUSPEND, SERIAL_ENDPOINT, entity=self._entity).wait()[0].result()

    def resume(self):
        logger.debug('Resuming serial port for entity {entity}'.format(entity=self._entity))
        self._messagebus.send_request(
            SERIAL_RESUME, SERIAL_ENDPOINT, entity=self._entity).wait()[0].result()


@CommandExtension(
    name='zserial',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SERIAL_PORT_IDS, required=True, instantiate_on=True),
        ConfigOption(SERIAL_ENABLED, required=True),
        ConfigOption(SERIAL_DEVICE, required=False),
        ConfigOption(SERIAL_BAUDRATE, required=False),
        ConfigOption(SERIAL_PROMPT, required=False),
        ConfigOption(SERIAL_FILTERS, required=False),
        ConfigOption(SERIAL_TIMEOUT, required=False),
        ConfigOption(SUT, required=False),
        ConfigOption(SUT_SERIAL_PORTS, required=False),
        ConfigOption(SUT_SERIAL_BAUDRATE, required=False),
        ConfigOption(SUT_SERIAL_DEVICE, required=False),
        ConfigOption(SUT_SERIAL_ENABLED, required=False),
        ConfigOption(SUT_SERIAL_FILTERS, required=False),
        ConfigOption(SUT_SERIAL_LOG_ENABLED, required=False),
        ConfigOption(SUT_SERIAL_PROMPT, required=False),
        ConfigOption(SUT_SERIAL_TIMEOUT, required=False),
    ],
    endpoints_and_messages={
        SERIAL_ENDPOINT: [
            SERIAL_SEND_COMMAND, LOG_LINE_RECEIVED, SERIAL_CONNECTION_LOST, SERIAL_CONNECTED,
            CRITICAL_EXTENSION_ERROR, SERIAL_RECONNECT, SERIAL_RAW_LINE, SERIAL_SUSPEND,
            SERIAL_RESUME
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
        self._entity = instances.get(SERIAL_PORT_IDS)

        self._device = None
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

            self._device, self._virtual = find_serial_port(device)

    def register_components(self, component_manager):
        if self._enabled:
            port = component_manager.get_unique_class_for_entity(self._entity)
            add_properties(port, 'serial', {
                'prompt': self._prompt,
                'timeout': self._timeout,
            })
            register_component = component(name='SerialPort', scope='session', can={self._entity})
            register_component(port, component_manager)

    @callback_dispatcher([BEFORE_COMMAND], [APPLICATION_ENDPOINT])
    @requires(messagebus='MessageBus')
    def before_command(self, message, messagebus):
        self._active = True
        self.open_serial_port(messagebus)

    @sequential_dispatcher(
        [SERIAL_SEND_COMMAND], [SERIAL_ENDPOINT], entity_option_id=SERIAL_PORT_IDS)
    def send_serial_command(self, message):
        data = message.data
        if isinstance(data, SendSerialCommandData):
            self._send_serial_command(data.line, event=data.event, timeout=data.timeout)
        else:
            self._send_serial_command(data)

    def _send_serial_command(self, line, event=None, timeout=None):
        if self._serial_connection is None:
            raise SerialException(
                (
                    'Error when trying to send serial command \'{line}\'. '
                    'Serial connection closed').format(line=line))

        if self._serial_connection.is_suspended():
            logging.warning(
                ('Ignoring command \'{line}\'. '
                 'Serial connection suspended').format(line=line))
        else:
            self._serial_connection.write_line(line)

        if event is not None:
            event.wait(timeout)

    @sequential_dispatcher([SERIAL_RAW_LINE], [SERIAL_ENDPOINT], entity_option_id=SERIAL_PORT_IDS)
    def handle_raw_line(self, message):
        raw_line = message.data
        self._serial_connection.parse_raw_line(raw_line)

    @callback_dispatcher([SERIAL_SUSPEND], [SERIAL_ENDPOINT], entity_option_id=SERIAL_PORT_IDS)
    def suspend(self, message):
        if self._serial_connection is None:
            raise SerialException(
                'Error when trying to suspend serial port: Serial connection closed')

        if self._serial_connection.is_suspended():
            raise SerialException('Trying to suspend a serial connection that is already suspended')

        self._serial_connection.suspend()
        return self._serial_connection.instance()

    @callback_dispatcher([SERIAL_RESUME], [SERIAL_ENDPOINT], entity_option_id=SERIAL_PORT_IDS)
    def resume(self, message):
        if self._serial_connection is None:
            raise SerialException(
                'Error when trying to resume serial port: Serial connection closed')

        if not self._serial_connection.is_suspended():
            raise SerialException('Trying to resume a serial connection that is not suspended')

        self._serial_connection.resume()

    @sequential_dispatcher(
        [SERIAL_CONNECTION_LOST, SERIAL_RECONNECT], [SERIAL_ENDPOINT],
        entity_option_id=SERIAL_PORT_IDS)
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
                    self._device, self._baudrate, self._virtual, self._timeout, messagebus,
                    self._entity, self._filters)
                logger.debug(
                    'Opened {device} for serial port {port}'.format(
                        device=self._device, port=self._entity))
                return
            except Exception:
                logger.debug(
                    'Failed to connect to serial port {port}'.format(port=self._entity),
                    exc_info=True)
                time.sleep(TIMEOUT_BETWEEN_CONNECTIONS)

        messagebus.trigger_event(CRITICAL_EXTENSION_ERROR, SERIAL_ENDPOINT, self._entity)

    def destroy(self):
        self.close_serial_port()

    def close_serial_port(self):
        if self._serial_connection:
            self._serial_connection.close()
            self._serial_connection = None


@FrameworkExtension(name='zserial', load_order=91, groups=['log_sources', 'serial'])
class SerialLogSourceExtension(AbstractExtension):

    def get_config(self, config, requested_config_options, requested_command_config_options):
        extension_config = {}
        for sut in config.get(SUT):
            if config.get(SUT_SERIAL_ENABLED, entity=sut):
                if config.get(SUT_SERIAL_PORTS, entity=sut):
                    raise MissingConditionalConfigOption(
                        'Mixing of sut and serial port id options is not supported!')
                add_sut_options_to_extension_config(sut, extension_config, config)
                sut_add_log_source(extension_config, sut, serial_log_line_entity(sut))
            else:
                for port in config.get(SUT_SERIAL_PORTS, entity=sut):
                    if config.get(SERIAL_ENABLED, entity=port) and config.get(SERIAL_LOG_ENABLED,
                                                                              entity=port):
                        sut_add_log_source(extension_config, sut, serial_log_line_entity(port))

        return ExtensionConfig(extension_config, 1, 'zserial')
