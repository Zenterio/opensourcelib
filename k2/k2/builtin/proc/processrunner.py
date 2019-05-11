import logging
import os
import pty
import re
import signal
import threading
import time
from subprocess import PIPE, Popen

from zaf.component.decorator import component
from zaf.extensions.extension import get_logger_name

logger = logging.getLogger(get_logger_name('k2', 'proc'))
logger.addHandler(logging.NullHandler())


@component(provided_by_extension='proc')
class ProcessRunner(object):
    r"""
    Component used to run subprocesses in a standardized way.

     .. code-block:: python

        @requries(process_runner='ProcessRunner')
        def test_with_process_runner(process_runner):
            process = process_runner('command --with --arguments', wait=False)
            process.write_stdin('input to process\n')
            process.wait(timeout=3)
            assert process.exit_code == 3
    """

    def __call__(
            self,
            command,
            env=None,
            cwd=None,
            shell=True,
            wait=True,
            expected_exit_code=0,
            timeout=None,
            stderr=PIPE):
        """
        Call to start a new process subprocesses.

        :param command: the command to run
        :param env: dict with additional environment variables to use when running command
        :param cwd: If not None change the current working directory for the process. Default None.
        :param shell: If the process should be started in a shell. Default True.
        :param wait: If this call should block until the process is completed. Default True.
        :param expected_exit_code: If wait=True the exit_code of the process will be asserted to this value.
        :param timeout: If wait=True this timeout will be used when waiting for the process to complete.
        :param stderr: The executed program's standard error file handle. (Same semantics as subprocess.)
        :return: Process object
        """
        return Process(command, env, cwd, shell, wait, expected_exit_code, timeout, stderr)


class Process(object):
    """Object representing a running processes."""

    def __init__(
            self,
            command,
            env=None,
            cwd=None,
            shell=True,
            wait=True,
            expected_exit_code=0,
            timeout=None,
            stderr=PIPE):
        """
        Start a process by running the command.

        :param command: the command to run
        :param env: dict with additional environment variables to use when running command
        :param cwd: If not None change the current working directory for the process. Default None.
        :param shell: If the process should be started in a shell. Default True.
        :param wait: If this call should block until the process is completed. Default True.
        :param expected_exit_code: If wait=True the exit_code of the process will be asserted to this value.
        :param timeout: If wait=True this timeout will be used when waiting for the process to complete.
        :param stderr: The executed program's standard error file handle. (Same semantics as subprocess.)
        """

        self._process = None
        self.stdout = ''
        self._stdout_data = []
        self.stderr = ''
        self._stderr_data = []
        self.exit_code = None

        self._stdin_fd, self._stdin_slave_fd = pty.openpty()

        new_env = os.environ.copy()
        if env:
            new_env.update(env)

        self._process = Popen(
            command,
            shell=shell,
            env=new_env,
            cwd=cwd,
            stdin=self._stdin_slave_fd,
            stdout=PIPE,
            stderr=stderr,
            universal_newlines=True,
            start_new_session=True)

        self.stdout_reader = threading.Thread(
            target=self._read_stream, args=('stdout', self._process.stdout, self._stdout_data))
        self.stdout_reader.start()
        if stderr == PIPE:
            self.stderr_reader = threading.Thread(
                target=self._read_stream, args=('stderr', self._process.stderr, self._stderr_data))
            self.stderr_reader.start()
        else:
            self.stderr_reader = None

        if wait:
            self.wait(timeout=timeout)
            assert self.exit_code == expected_exit_code, \
                'Expected exit_code {expected} but actual exit_code was {actual}'.format(
                    expected=expected_exit_code, actual=self.exit_code)

    def write_stdin(self, string, raw=False):
        """Write a string to stdin of the process."""
        if raw:
            os.write(self._stdin_fd, string)
        else:
            os.write(self._stdin_fd, string.encode('utf-8', 'ignore'))

    def _read_stream(self, name, source_stream, target_data):
        line = source_stream.readline()
        try:
            while line != '':
                stripped_line = line.rstrip()
                logger.debug('{name}: {line}'.format(name=name, line=stripped_line))
                target_data.append(stripped_line)
                line = source_stream.readline()

        except ValueError:
            # If stream is closed
            pass

    def wait(self, timeout=10.0):
        """Wait for the process to complete."""
        try:
            self.exit_code = self._process.wait(timeout=timeout)
            if self.stderr_reader is not None:
                self.stderr_reader.join(timeout=timeout)
            self.stdout_reader.join(timeout=timeout)
            self.stdout = '\n'.join(self._stdout_data)
            self.stderr = '\n'.join(self._stderr_data)
            logger.debug(
                '\n'.join(
                    [
                        '------------stdout--------------', self.stdout,
                        '------------stderr--------------', self.stderr,
                        '--------------------------------'
                    ]))

        except Exception as e:
            logger.error('Error while waiting for process to finish. Killing with SIGKILL')
            self.kill()
            raise e
        finally:
            self._close()

        return self.exit_code

    def kill(self):
        """Send kill signal to the process."""
        self.signal(signal.SIGKILL)

    def _close(self):
        try:
            os.close(self._stdin_fd)
        except OSError:
            pass

        try:
            os.close(self._stdin_slave_fd)
        except OSError:
            pass

    @property
    def pid(self):
        return self._process.pid

    @property
    def pgid(self):
        return os.getpgid(self._process.pid)

    def signal(self, sig):
        """Send signal to the process."""
        pid = self._process.pid
        logging.debug('Send signal sig={sig} to PID={pid}'.format(sig=sig, pid=pid))
        os.killpg(os.getpgid(pid), sig)

    def wait_for_match_in_stdout(self, regex, timeout=10.0):
        """
        Wait for the regex to match a line in stdout.

        :param regex: The regex to use
        :param timeout: The timeout
        :return: The match object for the the first found match
        """
        return self._wait_for_match_in_data(regex, 'stdout', timeout=timeout)

    def wait_for_match_in_stderr(self, regex, timeout=10.0):
        """
        Wait for the regex to match a line in stderr.

        :param regex: The regex to use
        :param timeout: The timeout
        :return: The match object for the the first found match
        """
        return self._wait_for_match_in_data(regex, 'stderr', timeout=timeout)

    def _wait_for_match_in_data(self, regex, data_name, timeout=10.0):
        """Wait for the regex to match a line in either stdout or stderr data."""
        if data_name == 'stdout':
            data = self._stdout_data
        else:
            data = self._stderr_data

        compiled_regex = re.compile(regex)
        next_line = 0
        deadline = time.time() + timeout

        while time.time() < deadline:
            if len(data) > next_line:
                match = compiled_regex.search(data[next_line])
                if match is not None:
                    return match
                next_line += 1
            else:
                time.sleep(0.05)

        msg = "No match for '{regex}' not found in {data_name} after {timeout} seconds".format(
            regex=regex, data_name=data_name, timeout=timeout)
        msg += '\noutput:\n' + '\n'.join(data)
        raise Exception(msg)
