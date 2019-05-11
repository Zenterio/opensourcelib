import subprocess
from unittest import TestCase

from testfixtures import Replacer
from testfixtures.popen import MockPopen

from ..executor import HostShellExecutor, HostShellExecutorError


class TestHostShellExecutor(TestCase):

    def setUp(self):
        self.original_communicate = MockPopen.communicate
        self.should_timeout = False
        self.actual_timeout = None

        def popen_communicate_with_timeout(input, timeout=None):
            self.actual_timeout = timeout
            if self.should_timeout:
                raise subprocess.TimeoutExpired('command', timeout)
            return self.original_communicate(input)

        MockPopen.communicate = popen_communicate_with_timeout
        self.Popen = MockPopen()
        self.replacer = Replacer()
        self.replacer.replace('subprocess.Popen', self.Popen)
        self.addCleanup(self.replacer.restore)
        self.exec = HostShellExecutor()

    def tearDown(self):
        MockPopen.communicate = self.original_communicate

    def test_if_not_provided_the_default_timeout_is_used(self):
        self.Popen.set_command('command')
        self.exec.send_line('command')
        assert self.actual_timeout == 60

    def test_if_provided_the_default_timeout_can_be_overriden(self):
        self.Popen.set_command('command')
        self.exec.send_line('command', timeout=30)
        assert self.actual_timeout == 30

    def test_raises_host_shell_executor_error_on_timeout(self):
        self.should_timeout = True
        self.Popen.set_command('command')
        with self.assertRaisesRegex(HostShellExecutorError, 'timed out'):
            self.exec.send_line('command', timeout=30)

    def test_can_specify_the_expected_exit_code(self):
        self.Popen.set_command('command', returncode=1)
        self.exec.send_line('command', expected_exit_code=1)

    def test_raises_host_shell_executor_error_on_unexpected_exit_code(self):
        self.Popen.set_command('command', returncode=2)
        with self.assertRaisesRegex(HostShellExecutorError, 'exit code'):
            self.exec.send_line('command', expected_exit_code=1)

    def test_the_contents_of_stdout_is_returned(self):
        stdout = 'this is my stdout content'
        self.Popen.set_command('command', stdout=stdout.encode('utf-8'))
        assert self.exec.send_line('command') == stdout

    def test_raises_host_shell_executor_error_if_stdout_contents_can_not_be_decoded(self):
        stdout = b'this is my \x80 stdout content'
        self.Popen.set_command('command', stdout=stdout)
        with self.assertRaisesRegex(HostShellExecutorError, "can't decode"):
            self.exec.send_line('command')

    def test_send_line_nowait(self):
        self.Popen.set_command('command')
        self.exec.send_line_nowait('command')

    def test_extended_process_information(self):
        stdout = 'this is my stdout content'
        stderr = 'this is my stderr content'
        exit_code = 2
        self.Popen.set_command(
            'command',
            stdout=stdout.encode('utf-8'),
            stderr=stderr.encode('utf-8'),
            returncode=exit_code)
        self.assertEqual(
            self.exec.send_line('command', extended_process_information=True),
            (stdout, stderr, exit_code))
