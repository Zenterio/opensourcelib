import logging
import subprocess

from zaf.extensions.extension import get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'hostshellexec'))
logger.addHandler(logging.NullHandler())


class HostShellExecutorError(Exception):
    pass


class HostShellExecutor(object):

    def __init__(self, timeout=60, encoding='utf-8'):
        self._timeout = timeout
        self._encoding = encoding

    def send_line(
            self, line, timeout=None, expected_exit_code=None, extended_process_information=False):
        timeout = timeout if timeout is not None else self._timeout

        try:
            logger.debug('Sending line: {line}'.format(line=line))
            process = self._send_line_nowait(line)
            stdout, stderr = process.communicate(timeout=timeout)
            stdout = stdout.decode(self._encoding)
            stderr = stderr.decode(self._encoding)
            for stdout_line in stdout.split('\n'):
                logger.debug(stdout_line)
        except Exception as e:
            raise HostShellExecutorError(str(e)) from None

        if expected_exit_code is not None and not process.returncode == expected_exit_code:
            raise HostShellExecutorError(
                (
                    'Command {command} exited with exit code {actual_exit_code}, '
                    'expected {expected_exit_code}').format(
                        command=line,
                        actual_exit_code=process.returncode,
                        expected_exit_code=expected_exit_code))

        if extended_process_information:
            return stdout, stderr, process.returncode
        else:
            return stdout

    def send_line_nowait(self, line):
        try:
            self._send_line_nowait(line)
        except Exception as e:
            raise HostShellExecutorError(str(e)) from None

    def _send_line_nowait(self, line):
        logger.debug('Running command: {line}'.format(line=line))
        return subprocess.Popen(line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
