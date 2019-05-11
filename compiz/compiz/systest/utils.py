import logging
import os
import re
import shlex
import subprocess
from glob import glob

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AssertCompizStartsMixin:

    def assert_compiz_starts(self):
        expected = 'usage: zcompiz [-h] {query,git}'
        self.assertIn(expected, invoke_for_output('zcompiz --help'))


class AssertInstalledMixin:

    def assert_installed(self, *programs):
        for program in programs:
            exit_code, *streams = invoke('which {program}'.format(program=program))
            self.assertEqual(exit_code, 0, '{program} is not installed.'.format(program=program))


def squeeze_whitespace(string):
    return re.sub('[\x00-\x20]+', ' ', string)


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
        shlex.split(command_line),
        env=env,
        cwd=cwd,
        shell=shell,
        stdin=subprocess.PIPE,
        stdout=stdout,
        stderr=stderr)
    out_buffers = popen.communicate(input='', timeout=5)
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
