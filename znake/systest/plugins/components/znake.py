import getpass
import logging
import os
import shutil
import signal
import subprocess
import threading
from subprocess import PIPE, Popen

import time
from k2.cmd.run import RUN_COMMAND
from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.builtin.logging import ENTER_LOG_SCOPE, LOG_DIR

from . import COVERAGE_CONFIG_FILE, COVERAGE_ENABLED, COVERAGE_REPORT

logger = logging.getLogger(get_logger_name('k2', 'znakecomponent'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    'znakecomponent',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(COVERAGE_CONFIG_FILE, required=False),
        ConfigOption(COVERAGE_ENABLED, required=False),
        ConfigOption(COVERAGE_REPORT, required=False),
    ])
class ZnakeComponent(AbstractExtension):

    def __init__(self, config, instances):
        root = getpass.getuser() == 'jenkins'

        @component(scope='test')
        @requires(workspace='Workspace')
        class ProjectDirectory(object):

            def __init__(self, project, workspace):
                self.project = project
                self.workspace = workspace

            def __enter__(self):
                os.rmdir(self.workspace.path)
                shutil.copytree(self.project, self.workspace.path)
                return self.workspace

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        @component(scope='test')
        class Znake(object):

            coverage_enabled = config.get(COVERAGE_ENABLED, False)
            coverage_config_file = config.get(COVERAGE_CONFIG_FILE)
            coverage_report = os.path.abspath(config.get(COVERAGE_REPORT))

            def __call__(
                    self,
                    command,
                    expected_exit_code=0,
                    wait_for_result=True,
                    file_logging=True,
                    workspace=None):

                if Znake.coverage_enabled:
                    config_file_arg = ''
                    if Znake.coverage_config_file:
                        config_file_arg = '--rcfile {file}'.format(file=Znake.coverage_config_file)

                    prefix = "COVEARGE_FILE={coverage_report} coverage run {config_file_arg} --parallel-mode".format(
                        coverage_report=self.coverage_report,
                        config_file_arg=config_file_arg)
                else:
                    prefix = ''

                znake_entry_point = subprocess.check_output(
                    ['which', 'znake'], universal_newlines=True).strip()

                znake_command = "{prefix} {entry_point} -e {root} {command}".format(
                    prefix=prefix,
                    entry_point=znake_entry_point,
                    root='--root' if root else '',
                    command=command)

                self.process_runner = ProcessRunner(
                    cwd=os.getcwd() if workspace is None else workspace.path,
                    env={k: v for k, v in os.environ.items() if k != 'BUILD_NUMBER'}
                )
                self.process_runner(znake_command)
                logger.info('command: {command}'.format(command=znake_command))

                if wait_for_result:
                    self.process_runner.wait()
                    assert self.process_runner.exit_code == expected_exit_code, \
                        'Expected exit code {expected} but actual code was {exit_code}'.format(
                            expected=expected_exit_code, exit_code=self.process_runner.exit_code)

                return self

            def wait(self, timeout=None):
                self.process_runner.wait(timeout=timeout)

            def kill(self):
                self.process_runner.kill()

            def waitfor(self, pattern, timeout=60.0, stderr=False):
                return self.process_runner.waitfor(pattern, timeout=timeout, stderr=stderr)

            @property
            def stdout(self):
                return self.process_runner.stdout

            @property
            def stderr(self):
                return self.process_runner.stderr

            @property
            def result(self):
                return self.process_runner.process

            @property
            def exit_code(self):
                return self.process_runner.exit_code


class ProcessRunner(object):

    def __init__(self, cwd, env=None):
        self.cwd = cwd
        self.process = None
        self.stdout = ''
        self._stdout_data = []
        self.stderr = ''
        self._stderr_data = []
        self.exit_code = None
        self.env = env

    def __call__(self, command):
        self.process = Popen(
            command,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            shell=True,
            universal_newlines=True,
            preexec_fn=os.setsid,
            cwd=self.cwd,
            env=self.env)

        self.stdout_reader = threading.Thread(
            target=self.read_stream, args=('stdout', self.process.stdout, self._stdout_data))
        self.stdout_reader.start()
        self.stderr_reader = threading.Thread(
            target=self.read_stream, args=('stderr', self.process.stderr, self._stderr_data))
        self.stderr_reader.start()
        return self.process

    def read_stream(self, name, source_stream, target_data):
        line = source_stream.readline()
        try:
            while line is not '' and not source_stream.closed:
                stripped_line = line.rstrip()
                logger.debug('{name}: {line}'.format(name=name, line=stripped_line))
                target_data.append(stripped_line)
                line = source_stream.readline()
        except ValueError:
            # If stream is closed from somewhere else when calling readline
            pass

    def wait(self, timeout=None):
        try:
            self.exit_code = self.process.wait(timeout=timeout)
            self.stderr_reader.join(timeout=timeout)
            self.stdout_reader.join(timeout=timeout)
            self.stdout = "\n".join(self._stdout_data)
            self.stderr = "\n".join(self._stderr_data)

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

    def kill(self):
        os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)

    def waitfor(self, pattern, timeout=60.0, stderr=False):
        if stderr:
            data = self._stderr_data
        else:
            data = self._stdout_data

        next_line = 0
        end_time = time.time() + timeout

        while time.time() < end_time:
            if len(data) > next_line:
                if pattern in data[next_line]:
                    return data[next_line]
                next_line += 1
            else:
                time.sleep(0.05)

        msg = "'{pattern}' not found in {pipe_name} after {timeout} seconds".format(
            pattern=pattern, pipe_name='stderr' if stderr else 'stdout', timeout=timeout)
        raise Exception(msg)
