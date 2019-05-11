import logging
import os
import shutil
from pathlib import Path
from subprocess import getstatusoutput
from tempfile import TemporaryDirectory
from time import localtime, strftime
from urllib.request import urlopen
from zipfile import ZipFile

from debpacker.common.ppa_list import retrieve_package_version_mapping
from debpacker.common.preparedassets import PreparedWorkspace, prepare_output_dir
from debpacker.common.templatehandling import import_template_dir
from debpacker.common.utils import create_deb_binary_package, create_deb_package_name, move, \
    remove_leading_slash, remove_trailing_slash, validate_deb_package_name

from .configuration import ToolchainDefinition
from .utils import DEFAULT_TOOLCHAIN_ROOT, DEFAULT_VERSION, GetToolchainException, ToolchainLink, \
    get_template_path

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def package_toolchain(
        uri,
        installation_paths,
        output_dir,
        force=False,
        workspace=None,
        version=DEFAULT_VERSION,
        package_name=None,
        toolchain_root=DEFAULT_TOOLCHAIN_ROOT,
        links=[],
        depends=[],
        create_dummy_archive=False):
    uri = remove_trailing_slash(uri)
    installation_paths = list(map(remove_trailing_slash, installation_paths))
    output_dir = remove_trailing_slash(output_dir)
    toolchain_root = remove_trailing_slash(remove_leading_slash(toolchain_root))
    package_name = package_name if package_name else _get_package_name(os.path.basename(uri))
    if not create_dummy_archive:
        validate_deb_package_name(package_name)
    with PreparedWorkspace(workspace, force) as (workspace, package_root):
        prepare_output_dir(output_dir)
        if create_dummy_archive is True:
            toolchain_root = ''
            toolchain_archive_path = _create_dummy_toolchain(workspace)
        else:
            toolchain_archive_path = _get_toolchain(uri, workspace)
        unpacked_toolchain_name = _unpack_toolchain(toolchain_archive_path, package_root)
        debian_directory = _import_debian_template(
            package_root, package_name, unpacked_toolchain_name, installation_paths, version,
            depends)
        _create_symlinks(
            package_root, unpacked_toolchain_name, map(os.path.basename, installation_paths))
        _add_debian_install_file(debian_directory, installation_paths, toolchain_root)
        _add_debian_links_file(debian_directory, links)
        deb_file = create_deb_binary_package(package_root)
        move(deb_file, output_dir, override=force)


def package_toolchain_list(
        toolchain_definitions: [ToolchainDefinition],
        output_dir: str,
        create_dummy_archives=False,
        report_created_toolchains=None):
    for index, definition in enumerate(toolchain_definitions):
        package_toolchain(
            definition.url,
            definition.paths,
            output_dir,
            version=definition.version,
            package_name=definition.name,
            toolchain_root=definition.toolchain_root,
            links=definition.links,
            depends=definition.depends,
            create_dummy_archive=create_dummy_archives)
        if report_created_toolchains:
            report_created_toolchains(index + 1)


def exclude_with_current_version(toolchain_definitions):
    """
    Exclude toolchains with the same version or lower as the current version in the PPA.

    Toolchains should be the same for all dists so this will exclude only those that
    matches the current version in all dist
    :param toolchain_definitions: list of toolchain definitions
    :return: the toolchains that have newer versions
    """
    toolchains = {}
    for dist, current_versions in retrieve_package_version_mapping().items():
        for toolchain in toolchain_definitions:
            if toolchain.name not in current_versions:
                logger.debug(
                    "Toolchain '{toolchain}' not found for {dist}".format(
                        toolchain=toolchain.name, dist=dist))
                toolchains[toolchain.name] = toolchain
            elif toolchain.version > current_versions[toolchain.name]:
                logger.debug(
                    "Toolchain '{toolchain}' for dist {dist} is newer than current PPA version '{version}'".
                    format(
                        toolchain=toolchain.name,
                        dist=dist,
                        version=current_versions[toolchain.name]))
                toolchains[toolchain.name] = toolchain
    return toolchains.values()


def _import_debian_template(
        package_root_dir, package_name, toolchain_name, install_path, version, depends):
    """
    Import debian template into the package_root_dir.

    :param package_root_dir: The dir to which the debian directory will be imported
    :param package_name: The name of the debain packge
    :param toolchain_name: The name of the toolchain
    :param install_path: The path where the toolchain is installed
    :param version: The version of the debian package
    :return: The path to the debian directory created from the template
    """
    template_arguments = {
        'PACKAGE_NAME': package_name,
        'SHORT_DESCRIPTION': 'Toolchain {toolchain}'.format(toolchain=toolchain_name),
        'LONG_DESCRIPTION': 'This toolchain is installed at {path}'.format(path=install_path),
        'VERSION': version,
        'TIME': strftime('%a, %d %b %Y %H:%M:%S +0000', localtime()),
        'DEPENDS': _format_depends(depends),
    }
    debian_template_dir = get_template_path('debian')
    debian_output_dir = import_template_dir(
        debian_template_dir, package_root_dir, **template_arguments)
    return debian_output_dir


def _format_depends(depends):
    return ', '.join(depends)


def _unpack_toolchain(toolchain_file_path, unpack_dir):
    """
    Unpack a toolchain at a given location into a destination directory.

    :param toolchain_file_path: Path to the toolchain
    :param unpack_dir: Path to the unpack directory
    :return: The name of the unpacked toolchain
    """
    logger.debug('Unpacking %s to %s', toolchain_file_path, unpack_dir)
    if os.path.isdir(toolchain_file_path):
        shutil.move(toolchain_file_path, unpack_dir)
        unpacked_toolchain_path = toolchain_file_path

    else:
        with TemporaryDirectory() as tmp_dir:
            shutil.unpack_archive(toolchain_file_path, tmp_dir)
            unpacked_toolchain_path = os.listdir(tmp_dir)[0]
            shutil.move(os.path.join(tmp_dir, unpacked_toolchain_path), unpack_dir)

    return os.path.basename(unpacked_toolchain_path)


def _create_symlinks(root: str, src: str, dst_list: [str]):
    """
    Create symlinks from src to dest in the root directory.

    :param root: Path to the directory where the toolchain_dir is located
    :param src: The name of the toolchain directory
    :param dst_list: Paths where the toolchain eventually will be installed
    """
    for destination in dst_list:
        path = os.path.join(root, destination)
        if not os.path.exists(path):
            os.symlink(os.path.abspath(os.path.join(root, src)), path, target_is_directory=True)


def _add_debian_install_file(debian_dir: str, destlist: [str], src_path):
    """
    Add an "install file" to a debian package located at the provided path.

    :param debian_dir: Path to the debian directory.
    :param destlist: Path to where the install directory should move it.
    :param src_path: A relative path that will be added to the src path
    """
    path = os.path.join(debian_dir, 'install')
    data = ''
    for dst in destlist:
        data += '{src} {dst}\n'.format(
            src=os.path.join(os.path.basename(dst), src_path), dst=os.path.dirname(dst))
    with open(path, 'w') as file:
        file.write(data)


def _add_debian_links_file(debian_dir: str, links: [ToolchainLink]):
    """
    Add a "links file" to a debian package located at the provided path.

    :param debian_dir: Path to the debian directory.
    :param links: A list containing ToolchainLink objects
    """
    path = os.path.join(debian_dir, 'links')
    with open(path, 'w') as file:
        file.write('\n'.join('{dst} {src}'.format(dst=dst, src=src) for src, dst in links))


def _create_dummy_toolchain(working_dir: str) -> str:
    """
    Create a new dummy toolchain archive.

    :param working_dir: Path to the directory to store the dummy in.
    :return: Path to the new dummy archive.
    """
    destination = os.path.join(working_dir, 'dummy_toolchain.zip')
    with ZipFile(destination, 'w') as z:
        z.writestr(os.path.join('dummy', 'info.txt'), 'This is a dummy toolchain.')
    return destination


def _get_toolchain(uri: str, working_dir: str) -> str:
    """
    Get a toolchain from a provided URI and copy it to the working_dir.

    The URI could be an URL or path to either a file or a directory.
    :param uri: URI to the toolchain.
    :param working_dir: Path to the directory where the toolchain will be stored
    :return: Path to the final destination of the toolchain.
    """
    uri = remove_trailing_slash(uri)
    dest_path = os.path.join(working_dir, os.path.basename(uri))
    if os.path.isdir(uri):
        # This is done with a subprocess call since I could not find a pythonic way to do this.
        command = 'cp -a {scr} {dst}'.format(scr=uri, dst=dest_path)
        status, output = getstatusoutput(command)
        if status != 0:
            msg = 'Could not get the toolchain with: {cmd}\n exit code: {code}\n output:\n{out}' \
                .format(cmd=command, code=status, out=output)
            raise GetToolchainException(msg)
        return dest_path

    if os.path.isfile(uri):
        uri = os.path.abspath(uri)
        uri = Path(uri).as_uri()
    logger.debug("Fetching toolchain from '%s' to '%s'", uri, dest_path)
    with urlopen(uri) as response, open(dest_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
        return dest_path


def _get_package_name(toolchain_uri):
    toolchain_uri = _remove_compressed_file_endings(toolchain_uri)
    return create_deb_package_name(toolchain_uri)


def _remove_compressed_file_endings(toolchain_uri: str):
    unpack_extensions = ['.tar.bz2', '.bz2', '.tar.gz', '.tgz', '.tar', '.zip'] + \
                        sum(map(lambda info: info[1], shutil.get_unpack_formats()), [])
    for extension in reversed(sorted(unpack_extensions, key=len)):
        if toolchain_uri.endswith(extension):
            return toolchain_uri.replace(extension, '')
    return toolchain_uri
