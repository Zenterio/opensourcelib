import fcntl
import logging
import os
import re

from serial import serial_for_url
from serial.threaded import LineReader, ReaderThread
from serial.tools.list_ports import comports
from zaf.extensions.extension import get_logger_name

from sutevents import LOG_LINE_RECEIVED
from zserial import SERIAL_CONNECTED, SERIAL_CONNECTION_LOST, SERIAL_ENDPOINT, SERIAL_RAW_LINE

logger = logging.getLogger(get_logger_name('k2', 'zserial'))

rawlogger = logging.getLogger('rawserial')
rawlogger.addHandler(logging.NullHandler())


class PortNotFound(Exception):
    pass


class SerialConnectionError(Exception):
    pass


class SerialConnectionWrapper(object):

    def __init__(self, thread, connection, serial, protocol_factory):
        self.thread = thread
        self.connection = connection
        self.serial = serial
        self.protocol_factory = protocol_factory

    def close(self):
        self.thread.close()

    def suspend(self):
        self.thread.stop()
        if self.thread.is_alive():
            raise SerialConnectionError('Failed to suspend serial thread')

    def resume(self):
        self.thread = ReaderThread(self.serial, self.protocol_factory)
        self.connection = self.thread.__enter__()

    def is_suspended(self):
        return not self.thread.is_alive()

    def write_line(self, line):
        logger.debug('Writing line to serial port: {line}'.format(line=line))
        self.connection.write_line(line)

    def parse_raw_line(self, line):
        self.connection.parse_raw_line(line)

    def instance(self):
        return self.serial


def start_serial_connection(port, baudrate, virtual, timeout, messagebus, entity, filters):
    serial_thread = None
    try:
        serial = serial_for_url(
            port, baudrate=baudrate, rtscts=virtual, dsrdtr=virtual, timeout=timeout)
        _lock_serial_port(serial)
        protocol_factory = _serial_connection(messagebus, entity, filters)
        serial_thread = ReaderThread(serial, protocol_factory)

        return SerialConnectionWrapper(
            serial_thread, serial_thread.__enter__(), serial, protocol_factory)
    except Exception as e:
        if serial_thread is not None:
            serial_thread.close()
        raise e


def _lock_serial_port(serial):
    """
    Acquire an exclusive lock for the serial port.

    While the lock is held, no other process may use the serial port.
    The lock may be acquired multiple times by the same process.
    The lock is automatically released when the process holding the lock exits.
    """
    try:
        fcntl.flock(serial.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        msg = 'Serial port {port} could not be locked. Is it already in use?'.format(
            port=serial.port)
        logger.debug(msg, exc_info=True)
        logger.error(msg)
        raise SerialConnectionError(msg)


def _serial_connection(messagebus_arg, entity_arg, inline_filters_arg=None):
    """
    Create a SerialConnection class.

    The class is embedded with references to the message bus and the entity
    to be used when sending messages.

    The inline_filters are used to fix faulty serial port lines.
    """

    class SerialConnection(LineReader):
        messagebus = messagebus_arg
        entity = entity_arg
        inline_filters = inline_filters_arg if inline_filters_arg else []

        def __init__(self):
            super().__init__()
            self.ENCODING = 'utf-8'
            self.UNICODE_HANDLING = 'strict'
            self.stack = []

            combined_filter = '|'.join(
                ['({filter})'.format(filter=filter) for filter in self.inline_filters])
            self.filter_pattern = re.compile(combined_filter) if inline_filters_arg else None

        def connection_made(self, transport):
            super().connection_made(transport)
            logger.debug('Serial connected for entity {entity}'.format(entity=self.entity))
            self.messagebus.trigger_event(SERIAL_CONNECTED, SERIAL_ENDPOINT, self.entity)

        def connection_lost(self, exc):
            logger.debug('Serial connection lost', exc_info=exc is not None)
            if exc is not None:
                # Only trigger SERIAL_CONNECTION_LOST on errors
                self.messagebus.trigger_event(
                    SERIAL_CONNECTION_LOST, SERIAL_ENDPOINT, self.entity, exc)

        def handle_line(self, line):
            """
            Handle a line from the serial port.

            Each line is sent as a LOG_LINE_RECEIVED message on the messagebus.

            Inline filters are used to filter out parts of a line and if the filtered content
            contains the end of the line the remaining part of the line is stored in a stack
            and combined with the next call to handle_line.
            The filtered out content is also sent out in their own LOG_LINE_RECEIVED messages.

            :param line: the line to handle
            """
            rawlogger.debug(line)
            self.messagebus.trigger_event(SERIAL_RAW_LINE, SERIAL_ENDPOINT, self.entity, line)

        def parse_raw_line(self, line):
            """Help method for handle_line to support recursive calls."""
            line = line.replace('\0', '')

            if len(self.stack) > 0:
                line = '{old}{new}'.format(old=self.stack.pop(), new=line)

            if self.filter_pattern:
                remaining, filtered, reached_end_of_line = _filter_line(line, self.filter_pattern)
                if filtered:
                    logger.debug(filtered)
                    self.messagebus.trigger_event(
                        LOG_LINE_RECEIVED, SERIAL_ENDPOINT, self.entity, filtered)
                    if reached_end_of_line:
                        self.stack.append(remaining)
                    else:
                        self.parse_raw_line(remaining)
                else:
                    logger.debug(remaining)
                    self.messagebus.trigger_event(
                        LOG_LINE_RECEIVED, SERIAL_ENDPOINT, self.entity, remaining)
            else:
                logger.debug(line)
                self.messagebus.trigger_event(LOG_LINE_RECEIVED, SERIAL_ENDPOINT, self.entity, line)

    return SerialConnection


def _filter_line(line, pattern):
    """
    Filter a line using the provided pattern.

    Only the the last match group will be filtered out and then the remaining line will be
    combined before and after the filtered match group.

    The result is a tuple with 3 elements
    1: The combined remaining line with the last match group filtered out
    2: The filtered out string
    3: If the filter reached the end of line

    :param line: the line to filter
    :param pattern: a regex with matchgroups for the things that should be filtered out
    :return: a tuple with (remaining, filtered, reached_end_of_line)
    """
    last_match = None
    for last_match in re.finditer(pattern, line):
        pass

    if last_match is None:
        return line, None, None

    start, end = last_match.span(last_match.lastindex)
    remaining = line[:start] + line[end:]
    filtered = line[start:end]
    reached_end_of_line = end == len(line)

    if remaining == '':
        return filtered, None, None
    else:
        return remaining, filtered, reached_end_of_line


def find_serial_port(device):
    """
    Use pyserial to find the serial port using the given device specification.

    :param device: the device to look for using port_info.name, device and location
                   special device value 'guess' can be used to get the first found device
    :return: Tuple containing the port and if the port is virtual
    :raises: PortNotFound if no matching serial port was found
    """
    if '://' in device:
        try:
            serial_for_url(device, do_not_open=True)
            return device, True
        except Exception as e:
            raise PortNotFound(
                'No port found using URL "{url}": {msg}'.format(url=device, msg=str(e)))

    selected_port_info = None
    for port_info in comports():
        if device == 'guess' or port_info.device == device or port_info.name == device or port_info.location == device:
            selected_port_info = port_info

    if selected_port_info is None:
        if os.path.exists(device):
            return device, True
        else:
            raise PortNotFound('No port found using device {device}'.format(device=device))
    else:
        return selected_port_info.device, False
