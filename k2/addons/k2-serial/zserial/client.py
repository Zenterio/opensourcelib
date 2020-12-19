import logging
import re
import threading
import time
from queue import Empty

from zaf.extensions.extension import get_logger_name
from zaf.messages.dispatchers import LocalMessageQueue

from sutevents import LOG_LINE_RECEIVED
from zserial import SERIAL_ENDPOINT, SERIAL_SEND_COMMAND

from .messages import SendSerialCommandData

logger = logging.getLogger(get_logger_name('k2', 'zserial'))
logger.addHandler(logging.NullHandler())


class SerialError(Exception):
    pass


class SerialClient(object):
    """
    Communicates with the serial extension to send command over serial connection.

    Helps with parsing output by prefixing all lines of the response on the server
    to make it possible to parse them from the LOG_LINE_RECEIVED messages
    """

    # ID to keep track use for prefixing command output
    command_id = 0
    command_id_lock = threading.Lock()
    input_overrun_pattern = re.compile(r'tty.* (?P<count>\d+) input overrun\(s\)')

    def __init__(self, messagebus, entity, timeout=10, endmark=' # '):
        """
        Initialize the serial client.

        Because of how the messagebus works, the SUT entity is needed to
        communicate with the correct instance of the serial extension.

        :param messagebus: the messagebus to use to communicate with the serial extension
        :param entity: the messagebus entity of the serial extension instance
        :param timeout: default timeout to use during commands
        :param endmark: default endmark to look for when sending commands
        """
        self.messagebus = messagebus
        self.entity = entity
        self.default_timeout = timeout
        self.default_endmark = re.compile(endmark)

    def send_line(
            self,
            line,
            timeout=None,
            endmark=None,
            expected_exit_code=None,
            prefix_output=True,
            retry_once=False,
            extended_process_information=False):
        """
        Send a line using the serial connection and waits for response.

        Default behaviour is to make the server prefix each response line and
        to inject a custom endmark. This requires the server to run a shell.
        Setting prefix_output to false will remove this default behaviour.

        Endmark will be generated for prefix_output=True but it can also be set manually.

        :param line: the line to send
        :param timeout: the timeout when waiting for response
        :param endmark: the endmark to look for when parsing response
        :param expected_exit_code: If specified a SerialError is sent if the exit code is different
                                   than the expected exit code. Requires prefix_output to be True.
        :param prefix_output: if shell functionality should be used to prefix the output
                              and make it easier to parse
        :param retry_once: Not used - provided for compatibility with telnet exec
        :param extended_process_information: Instead of the default return value, return a tuple
                                             containing (stdout + stderr, '', exit_code).
        :return: Combined stdout and stderr of the command
        """
        command_prefix = ''
        echo_exit_code_as_last_line = False
        exit_code = None

        if prefix_output:
            command_prefix = self._get_command_prefix()

            line = "{{ {line} ; echo exit_code=$?; }} 2>&1 | sed -e 's/^/{prefix}/'".format(
                line=line, prefix=command_prefix)

            if not endmark:
                line += " && PREFIX='{prefix}' && echo end_$PREFIX".format(
                    prefix=command_prefix.strip())
                echo_exit_code_as_last_line = True
                endmark = 'end_{prefix}'.format(prefix=command_prefix.strip())

        if not endmark:
            endmark = self.default_endmark
        else:
            endmark = re.compile(endmark)

        timeout = timeout if timeout is not None else self.default_timeout
        start_time = time.time()
        with LocalMessageQueue(self.messagebus, [LOG_LINE_RECEIVED], [SERIAL_ENDPOINT],
                               [self.entity]) as queue:
            serial_send_data = SendSerialCommandData(line, timeout)
            try:
                serial_send_response = self.messagebus.send_request(
                    SERIAL_SEND_COMMAND, SERIAL_ENDPOINT, self.entity, serial_send_data)

                if not serial_send_response:
                    msg = (
                        'No serial extension received command \'{command}\': '
                        'Serial connection might not be active').format(command=line)
                    logger.critical(msg)
                    raise SerialError(msg)

                lines = []
                received_line = ''
                error = None
                while not endmark.search(received_line):
                    try:
                        received_line = queue.get(
                            timeout=max(0.1, timeout - (time.time() - start_time))).data
                    except Empty as e:
                        error = e

                    if error or time.time() - start_time > timeout:
                        msg = 'Timeout waiting for response when sending line {line}. ' \
                              'Expected {endmark}, last received line is {received_line}'.format(
                                line=line, endmark=endmark, received_line=received_line)
                        logger.error(msg)
                        raise TimeoutError(msg)

                    match = self.input_overrun_pattern.search(received_line)
                    if match:
                        msg = 'TTY input overrun. {count} characters were dropped.'.format(
                            count=match.groupdict()['count'])
                        logger.error(msg)
                        raise SerialError(msg)

                    if extended_process_information or expected_exit_code is not None:
                        if exit_code is None:
                            exit_code = self._get_exit_code(command_prefix, received_line)
                        if exit_code and expected_exit_code is not None:
                            self._check_exit_code(exit_code, expected_exit_code)

                    if received_line.startswith(
                            command_prefix) and not endmark.search(received_line):
                        lines.append(received_line.replace(command_prefix, ''))
            finally:
                serial_send_data.event.set()

            if echo_exit_code_as_last_line:
                lines = lines[0:-1]

            for index, line in enumerate(lines):
                logger.debug('Command response line {index}: {line}'.format(index=index, line=line))

            if extended_process_information:
                return ('\n'.join(lines), '', exit_code)
            return '\n'.join(lines)

    def _get_command_prefix(self):
        with SerialClient.command_id_lock:
            SerialClient.command_id += 1
            command_id = SerialClient.command_id

            return 'cmd:{id}: '.format(id=command_id)

    def send_line_nowait(self, line):
        """
        Send a line to the serial connection without waiting for response.

        :param line: the line to send
        """
        self.messagebus.send_request(SERIAL_SEND_COMMAND, SERIAL_ENDPOINT, self.entity, line)

    def _get_exit_code(self, prefix, line):
        match = re.search(r'{prefix}exit_code=(\d+)'.format(prefix=prefix), line)
        return int(match.group(1)) if match else None

    def _check_exit_code(self, exit_code, expected_exit_code):
        if exit_code != int(expected_exit_code):
            msg = (
                'Unexpected exit code {exit_code} when running command. '
                'Expected was {expected}').format(
                    exit_code=exit_code, expected=expected_exit_code)
            logger.error(msg)
            raise SerialError(msg)
