import logging
import os
import shlex
import subprocess
import sys
from contextlib import contextmanager
from glob import glob
from string import Template
from tempfile import TemporaryDirectory
from unittest.mock import ANY

from debpacker.common.test.utils import AssertFileContainsMixin, AssertFileNotExistsMixin
from debpacker.common.utils import get_file_relative_root

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AssertZdebPackerStartsMixin:

    def assert_zdeb_packer_starts(self):
        expected = 'Usage: zdeb-packer [OPTIONS] COMMAND [ARGS]...'
        self.assertIn(expected, invoke_for_output('zdeb-packer --help'))


class AssertInstalledMixin:

    @staticmethod
    def assert_installed(*programs):
        for program in programs:
            exit_code, *streams = invoke('which {program}'.format(program=program))
            assert exit_code == 0, '{program} is not installed.'.format(program=program)


class AssertCorrectToolchainMixin(AssertFileContainsMixin, AssertFileNotExistsMixin):

    def assert_correct_toolchain(
            self, deb_path, package_name, toolchain_files, toolchain_file_content):

        install(deb_path)
        for path in toolchain_files:
            self.assert_file_contains(path, toolchain_file_content)
        uninstall(package_name)
        for path in toolchain_files:
            self.assert_file_not_exists(path)


def uninstall(package_name):
    invoke_for_output('sudo dpkg -P {name}'.format(name=package_name), expected_exit_code=ANY)


def install(deb_path):
    AssertInstalledMixin.assert_installed('gdebi')
    assert os.path.isfile(deb_path), 'The file does not exists: {path}'.format(path=deb_path)
    invoke_for_output('sudo gdebi --non-interactive {path}'.format(path=deb_path))


def running_with_tty():
    return sys.stdin.isatty()


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
            'Bad exit code ({code} instead of {expected}):\n{console}'.format(
                code=exit_code, expected=expected_exit_code, console=stdout))
    return stdout


class InstallTestMixin(AssertInstalledMixin):

    package = ''

    def install_test_setup(cls):
        cls.assert_installed('gdebi')
        uninstall(cls.package)

    def assert_starts(self):
        raise NotImplementedError()

    def test_install(self):
        deb = get_deb_path('{package}_*.deb'.format(package=self.package), False)
        install(deb)
        self.assert_starts()


class UpgradeTestMixin(AssertInstalledMixin):

    binary = ''
    package = ''

    def upgrade_test_setup(self):
        self.assert_installed('gdebi')
        uninstall(self.package)
        self.original_version = None

    def assert_starts(self):
        raise NotImplementedError()

    def install(self, upgrade_version=False):
        deb = get_deb_path('{package}_*.deb'.format(package=self.package), upgrade_version)
        install(deb)

    def store_versions(self):
        self.original_version = invoke_for_output('{bin} --version'.format(bin=self.binary))

    def assert_higher_version_installed(self):
        upgrade_version = invoke_for_output('{bin} --version'.format(bin=self.binary))
        self.assertGreater(upgrade_version, self.original_version)

    def test_upgrade(self):
        self.install(upgrade_version=False)
        self.store_versions()
        self.install(upgrade_version=True)
        self.assert_higher_version_installed()
        self.assert_starts()


def get_test_data(*path):
    return get_file_relative_root(__file__, 'data', *path)


@contextmanager
def prepare_template(path, **kwargs):
    with TemporaryDirectory() as temp_dir:
        out_path = os.path.join(temp_dir, os.path.basename(path))
        with open(path) as template_file, open(out_path, 'w') as file:
            file.write(Template(template_file.read()).substitute(kwargs))
        yield out_path


def is_hard_link(file1, file2):
    stat1 = os.stat(file1)
    stat2 = os.stat(file2)
    return (stat1.st_ino, stat1.st_dev) == (stat2.st_ino, stat2.st_dev)
