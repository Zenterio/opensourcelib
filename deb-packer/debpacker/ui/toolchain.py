import logging
import os
from itertools import starmap
from urllib.error import URLError

import click
from progressbar import ETA, Bar, Percentage, ProgressBar, SimpleProgress
from voluptuous import MultipleInvalid

from debpacker import toolchain
from debpacker.common.preparedassets import OutputExists, WorkspaceExists

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

COULD_NOT_FETCH_TOOLCHAIN_MESSAGE = \
    'Problem with the connection while fetching the toolchains. Is the URI valid?'


@click.command(name='toolchain', help='Creating toolchain debian package')
@click.option(
    '--uri', '-u', required=True, help='Path or URL to toolchain archive', metavar='<uri>')
@click.option(
    '--dummy', default=False, is_flag=True, help='Creates a dummy instead of using a real archive.')
@click.option(
    '--installation-path',
    '-p',
    required=True,
    multiple=True,
    metavar='<path>',
    help='Path(s) to install toolchain. Can be specified multiple times')
@click.option(
    '--output-dir',
    '-o',
    default=os.getcwd,
    type=click.Path(),
    metavar='<path>',
    help='The directory where the resulting deb file will be placed. Defaults to cwd.')
@click.option(
    '--workspace',
    '-w',
    metavar='<path>',
    help='Workspace directory. If not given then a temporary directory will be created')
@click.option(
    '--deb-version',
    '-v',
    default=toolchain.DEFAULT_VERSION,
    metavar='<version>',
    help='The version of the toolchain package.')
@click.option(
    '--force', '-f', default=False, is_flag=True, help='Force overwriting of files and directories')
@click.option(
    '--toolchain-root',
    '-tr',
    default=toolchain.DEFAULT_TOOLCHAIN_ROOT,
    metavar='<root>',
    help='A relative path inside the toolchain directory to the actual root of the toolchain.')
@click.option(
    '--link',
    '-l',
    default=[],
    nargs=2,
    multiple=True,
    metavar='<src> <dst>',
    help='Link(s) to be installed by the toolchain. Can be specified multiple times.')
@click.option(
    '--depends',
    '-d',
    default=[],
    multiple=True,
    metavar='<dependency>',
    help='Runtime dependencies of the package')
def package_toolchain(
        uri, dummy, installation_path, output_dir, workspace, deb_version, force, toolchain_root,
        link, depends):
    try:
        toolchain.package_toolchain(
            uri,
            installation_path,
            output_dir,
            force=force,
            workspace=workspace,
            version=deb_version,
            toolchain_root=toolchain_root,
            links=list(starmap(toolchain.ToolchainLink, link)),
            depends=depends,
            create_dummy_archive=dummy)
    except (OutputExists, WorkspaceExists) as e:
        logger.debug(e, exc_info=True)
        logger.error(e)
        exit(1)
    except URLError as e:
        logger.debug(e, exc_info=True)
        logger.error(COULD_NOT_FETCH_TOOLCHAIN_MESSAGE)
        exit(1)
    except Exception as e:
        logger.debug(e, exc_info=True)
        logger.error(e)
        exit(1)


@click.command(name='toolchain-list')
@click.option(
    '--file', '-f', required=True, type=click.File(), help='Path to the toolchain definition file')
@click.option(
    '--dummy', default=False, is_flag=True, help='Creates dummies instead of using real archives.')
@click.option(
    '--output-dir',
    '-o',
    default=os.getcwd,
    type=click.Path(),
    help='The directory where the resulting deb files will be placed. Defaults to cwd.')
@click.option(
    '--only-newer-versions',
    '-n',
    is_flag=True,
    required=False,
    default=False,
    help='Package only versions that are newer than the ones existing in Zenterio PPA')
@click.option('--quiet', '-q', is_flag=True, default=False, help='No output')
def package_toolchain_list(file, dummy, output_dir, only_newer_versions, quiet):
    """
    Create one or several toolchain(s) from a toolchain definition file.

    \b
    The definition language used is yaml and the format looks like this:
    ===================================
    name: <toolchain name>
    url: <url to toolchain>
    paths: <path or list of paths>
    version: <version>
    toolchain_root: <relative root inside the downloaded toolchain>
    links: <mapping from link src>:  <to link dst>
    depends: <dependency or list of dependencies>
    ---
    name: zenterio-toolchain
    url: ftp://path
    paths:
      - /opt/tools/toolchain1.4.89
      - /opt/toolchain/toolchain1.4.89
    version: 1.0.0
    links:
        /usr/bin/script: /opt/toolchain/toolchain1.4.89/bin/script
    depends:
      - gdb
    other_ignored_key: with some value
    ===================================

    Attributes other than NAME, URL, PATHS, VERSION, LINKS and DEPENDS are ignored.
    """
    try:
        definitions = toolchain.ToolchainDefinitionsParser().parse(file)
        if only_newer_versions:
            definitions = toolchain.exclude_with_current_version(definitions)

        progress_function = None if quiet else get_progress_bar(len(definitions)).update
        toolchain.package_toolchain_list(
            definitions,
            output_dir,
            create_dummy_archives=dummy,
            report_created_toolchains=progress_function)
    except (OutputExists, WorkspaceExists) as e:
        logger.debug(e, exc_info=True)
        logger.error(e)
        exit(1)
    except MultipleInvalid as e:
        logger.debug(e, exc_info=True)
        logger.error(e)
        exit(1)
    except URLError as e:
        logger.debug(e, exc_info=True)
        logger.error(COULD_NOT_FETCH_TOOLCHAIN_MESSAGE)
        exit(1)
    except Exception as e:
        logger.debug(e, exc_info=True)
        logger.error(e)
        exit(1)
    finally:
        file.close()


def get_progress_bar(max_value=100):
    widgets = [Percentage(), ' (', SimpleProgress(), ')', Bar(), ETA()]
    bar = ProgressBar(max_value=max_value, redirect_stdout=True, widgets=widgets)
    bar.start()
    return bar
