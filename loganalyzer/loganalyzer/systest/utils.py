import logging
import os
import shlex
import subprocess
from glob import glob

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AssertLoganalyzerStartsMixin:

    def assert_loganalyzer_starts(self):
        self.exec_proc_and_baseline_check([
            'zloganalyzer',
            '--help',
        ], 'help.txt')


def assert_installed(*programs):
    for program in programs:
        exit_code, *streams = invoke('which {program}'.format(program=program))
        if exit_code != 0:
            raise AssertionError('{program} is not installed.'.format(program=program))


def get_os_codename():
    return invoke_for_output('lsb_release -c').strip('Codename:').strip()


def get_deb_path(deb_glob, upgrade_version):
    dist_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'dist', get_os_codename())
    if upgrade_version:
        dist_dir = os.path.join(dist_dir, 'upgrade')
    return glob(os.path.join(dist_dir, deb_glob))[0]


def invoke(
        command_line: str,
        *,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
        cwd=None,
        shell=False):

    logger.debug(command_line)
    popen = subprocess.Popen(
        shlex.split(command_line), env=env, cwd=cwd, shell=shell, stdout=stdout, stderr=stderr)
    out_buffers = popen.communicate()
    stdout = out_buffers[0].decode('utf-8') if out_buffers[0] is not None else ''
    stderr = out_buffers[1].decode('utf-8') if out_buffers[1] is not None else ''
    exit_code = popen.returncode
    return exit_code, stdout, stderr


def invoke_for_output(command_line: str, expected_exit_code=0, **kwargs):
    kwargs = {key: value for key, value in kwargs.items() if value is not None}
    exit_code, stdout, stderr = invoke(command_line, stderr=subprocess.STDOUT, **kwargs)
    if exit_code != expected_exit_code:
        raise ValueError(
            'Bad exit code ({code} instead of {expected}): {console}'.format(
                code=exit_code, expected=expected_exit_code, console=stdout))
    return stdout
