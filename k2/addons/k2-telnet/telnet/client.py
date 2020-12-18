import logging
import re

import pexpect
from zaf.extensions.extension import get_logger_name


class LoggerFile:

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.buffer = ''

    def write(self, s):
        self.buffer += s
        try:
            while True:
                i = self.buffer.index('\n')
                self.logger.log(self.level, self.buffer[:i])
                self.buffer = self.buffer[i + 1:]
        except ValueError:
            pass

    def flush(self):
        pass

    def close(self):
        if self.buffer:
            self.logger.log(self.level, self.buffer)
            self.buffer = ''


def _regex_as_string(r):
    """Coerce a regex string or a compiled regex into a regex string."""
    return getattr(r, 'pattern', r)


class TelnetError(Exception):
    """Raised when something has gone wrong with a telnet session."""
    pass


class TelnetTimeout(Exception):
    """Raised when a timeout has occured."""
    pass


class TelnetClient(object):
    """
    Communicates with a remote host using the telnet protocol.

    Uses pexpect to spawn a telnet subprocess. Assumes the telnet command is
    available on the host system. Provides facilities for sending commands to
    a remote host and means of searching for specific outputs in response.
    """

    # Default marker to look for in the remote host output after each command.
    DEFAULT_END_MARK = r'.* # '

    # Numer of seconds to wait before considering a command to have timed-out.
    DEFAULT_TIMEOUT = 60

    # Dimensions of the telnet terminal window. Set this to something large.
    # Output from the remote host that is larger than these dimensions may
    # contain newlines or be paginated.
    DEFAULT_TERMINAL_DIMENSIONS = (24, 9999)

    def __init__(
            self, ip, port=23, timeout=DEFAULT_TIMEOUT, endmark=DEFAULT_END_MARK, context_name=''):
        self.ip = ip
        self.port = port
        self.telnet = None
        self.timeout = timeout
        self.endmark = re.compile(endmark) if endmark is not None else None
        if context_name:
            context_name = '.' + context_name
        self.logger = logging.getLogger(get_logger_name('k2', 'telnet') + context_name)
        self.logger.addHandler(logging.NullHandler())
        self.rawlogger = logging.getLogger('rawtelnet' + context_name)
        self.rawlogger.addHandler(logging.NullHandler())
        self.rawlogger_file = None

    @property
    def process(self):
        return self.telnet

    def connect(self):
        if self.is_connected():
            self.disconnect()
        try:
            self.logger.debug('Connecting to {ip}'.format(ip=self.ip))
            self.rawlogger_file = LoggerFile(self.rawlogger, logging.DEBUG)
            self.telnet = pexpect.spawnu(
                'telnet {ip} {port}'.format(ip=self.ip, port=self.port),
                timeout=self.timeout,
                dimensions=self.DEFAULT_TERMINAL_DIMENSIONS,
                logfile=self.rawlogger_file)
            # This is a workaround. We want to ensure that the telnet shell
            # is ready to accept a command. If we give it a command at the
            # wrong time the echoes and output become unreliable. Also, telnet
            # will send a ESC[J clear screen sequence after the first prompt,
            # so we send a dummy test command whos output may get affected by it.
            # This ensures that the following "real" commands do not get affected by this.
            self.telnet.expect([self.endmark], timeout=self.timeout)
            self._send_line('echo TEST')
            self.telnet.expect(['TEST'], timeout=self.timeout)
            self.telnet.expect([self.endmark], timeout=self.timeout)
        except Exception:
            self.telnet = None
            if self.rawlogger_file is not None:
                self.rawlogger_file.close()
                self.rawlogger_file = None
            raise TelnetError('Connection to {ip}:{port} failed'.format(ip=self.ip, port=self.port))
        self.logger.info('Connection to {ip}:{port} established'.format(ip=self.ip, port=self.port))

    def disconnect(self):
        if self.telnet is not None:
            self.logger.debug('Disconnecting from {ip}:{port}'.format(ip=self.ip, port=self.port))
            self.telnet.close(force=False)
            self.telnet = None
        if self.rawlogger_file is not None:
            self.rawlogger_file.close()
            self.rawlogger_file = None

    def is_connected(self):
        return self.telnet is not None and self.telnet.isalive()

    def _ensure_connected(self):
        if not self.is_connected():
            self.connect()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *exc_details):
        self.disconnect()

    def send_line(
            self,
            line,
            timeout=None,
            endmark=None,
            expected_exit_code=None,
            retry_once=True,
            extended_process_information=False):
        """
        Send a line to the remote host.

        Raises TelnetError on communication error.
        Raises TelnetTimeout if the end marker is not seen before time-out.

        Optionally checks that the exit code after executing the line.
        Raises TelnetError if the exit code is not the expected value.

        By default, if there was an TelnetError sending the line, it will retry sending the line again.

        Returns a string containing the remote hosts output before the end marker.

        :param line: the line to send.
        :param timeout: the timeout when waiting for response.
        :param endmark: the endmark to look for when parsing response.
        :param expected_exit_code: If specified, a TelnetError is sent if the exit code is different
                                   than the expected exit code.
        :param retry_once: Retry (once) if an TelnetError occurs while sending the line. It does not
                           apply to checking the exit code or timeouts.
        :param extended_process_information: Instead of the default return value, return a tuple
                                             containing (stdout + stderr, '', exit_code).
        :return: the command output.
        """
        self._ensure_connected()

        try:
            endmark = self.endmark if endmark is None else endmark
            timeout = self.timeout if timeout is None else timeout
            self._send_line(line)
            self.expect([re.escape(line)], timeout=timeout)
            self.expect([endmark], timeout=timeout)

            output = self.telnet.before
            self.logger.debug('Output before endmark: {output}'.format(output=output))
        except (TelnetError, pexpect.ExceptionPexpect) as e:
            if retry_once:
                msg = 'Caught exception {e}, retrying once more.'.format(e=str(e))
                self.logger.debug(msg, exc_info=True)
                self.logger.warning(msg)
                return self.send_line(line, timeout, endmark, expected_exit_code, retry_once=False)
            else:
                raise
        if extended_process_information or expected_exit_code is not None:
            exit_code = self._get_exit_code(endmark, timeout)
            if expected_exit_code is not None:
                self._check_exit_code(exit_code, expected_exit_code)
        if extended_process_information:
            return (output, '', exit_code)
        return output

    def send_line_nowait(self, line):
        """
        Similar to send_line() but performs fewer checks.

        Instead of checking that the endmarker is printed, the process exit code
        and collecting output from the remote host, returns immediately.
        """
        self._ensure_connected()

        self._send_line(line)
        self.expect([re.escape(line)], timeout=self.timeout)

    def expect(self, patterns, timeout=None):
        """
        Expect one or more patterns to be present in the remote hosts output.

        Takes a list of regular expressions describing output to look for. Will
        block until a match is found or until the time-out is reached.

        Raises TelnetError on communication error.
        Raises TelnetTimeout no match is found before time-out.

        Returns the position in the patterns list of the pattern that matched.
        """
        timeout = self.timeout if timeout is None else timeout
        if not self.is_connected():
            raise TelnetError('Can not expect patterns while disconnected')
        try:
            self.logger.debug('Waiting for patterns: {patterns}'.format(patterns=patterns))
            result = self.telnet.expect(patterns, timeout=timeout)
            return result
        except pexpect.EOF:
            self.disconnect()
            raise TelnetError('Connection to {ip}:{port} lost'.format(ip=self.ip, port=self.port))
        except pexpect.TIMEOUT:
            raise TelnetTimeout('Timeout waiting for a pattern')

    def _send_line(self, line):
        if not self.is_connected():
            raise TelnetError('Can not send lines while disconnected')
        try:
            self.logger.info('Sending line: {line}'.format(line=line))
            self.telnet.sendline(line)
        except pexpect.EOF:
            self.disconnect()
            raise TelnetError('Connection to {ip}:{port} lost'.format(ip=self.ip, port=self.port))

    def _get_exit_code(self, endmark, timeout):
        self.logger.debug('Checking exit code')
        self.telnet.sendline('echo $?')
        self.expect([r'\d+'], timeout=timeout)
        exit_code = self.telnet.match.group(0)
        self.expect([endmark], timeout=timeout)
        return int(exit_code)

    def _check_exit_code(self, exit_code, expected_exit_code):
        if exit_code != expected_exit_code:
            raise TelnetError(
                'Unexpected exit code when running command. Expected {e} got {a}'.format(
                    e=expected_exit_code, a=exit_code))
