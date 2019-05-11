import glob
import logging
import os
import shlex
import shutil
import string
import subprocess

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class InvalidPackageNameException(Exception):
    pass


def create_deb_binary_package(package_root: str) -> str:
    """
    Create a debian package.

    :param package_root: The root of the debian package. This is also the dir in which the debian/ dir is located.
    :return: The path to the created debian file
    """
    invoke_for_output('dpkg-buildpackage -b -us -uc', cwd=package_root)
    deb_file = glob.glob(os.path.join(package_root, '..', '*.deb'))[0]
    return deb_file


def create_deb_equivs_package(equivs_file):
    package_root = os.path.dirname(equivs_file)
    logger.debug(
        invoke_for_output(
            'equivs-build {path}'.format(path=os.path.basename(equivs_file)), cwd=package_root))
    deb_file = glob.glob(os.path.join(package_root, '*.deb'))[0]
    return deb_file


def validate_deb_package_name(name):
    new_name = create_deb_package_name(name)
    if name != new_name:
        raise InvalidPackageNameException(
            'Package name "{name}" is invalid (change suggestion: "{new_name}")'.format(
                name=name, new_name=new_name))

    return True


def create_deb_package_name(name):
    if not name:
        raise InvalidPackageNameException(
            'Package name "{name}" is invalid (empty)'.format(name=name))

    invalid_symbols = set(name).difference(set(' _-.' + string.digits + string.ascii_letters))
    if invalid_symbols:
        raise InvalidPackageNameException(
            'Package name "{name}" is invalid (contains unsupported symbols "{symbols}")'.format(
                name=name, symbols=invalid_symbols))

    if not name.startswith('zenterio-'):
        name = 'zenterio-' + name

    for symbol in ['_', ' ']:
        name = name.replace(symbol, '-')
    return name.lower()


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


def move(src, dst, override=False):
    logger.debug('Moving file from {src} to {dst}'.format(src=src, dst=dst))
    if override and os.path.isdir(dst):
        dst_path = os.path.join(dst, os.path.basename(src))
        if os.path.isfile(dst_path):
            os.remove(dst_path)
    shutil.move(src, dst)


def get_all_files(root):
    for root, dirs, files in os.walk(root):
        for file in files:
            yield os.path.join(root, file)


def normalize_path(path):
    if path:
        return os.path.normpath(path)


def remove_trailing_slash(uri: str):
    return uri.rstrip('/')


def remove_leading_slash(string: str):
    return string.lstrip('/')


def get_file_relative_root(root, *path):
    path = os.path.join(os.path.dirname(root), *path)
    assert os.path.exists(path), 'No file could be found at: {path}'.format(path=path)
    return path
