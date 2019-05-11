import logging
import os

import click

from debpacker import metapackage

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@click.command(name='metapackage')
@click.option(
    '--output-dir',
    '-o',
    default=os.getcwd,
    type=click.Path(),
    help='The directory where the resulting deb file will be placed. Defaults to cwd.')
@click.option('--workspace', '-w', help='Workspace directory. Defaults to a new temp directory.')
@click.option(
    '--force',
    '-f',
    default=False,
    is_flag=True,
    help='Force overwriting of the working directory.')
@click.argument('package-description', type=click.Path(), metavar='<package-description>')
def create_metapackage(output_dir, workspace, force, package_description):
    """
    Target that creates meta packages, i.e. a debian package which only perpose is to "include" other packages.

    The resulting .deb file will be placed under the <output-dir>/dist directory if the config option
    "distributions" is empty.

    If the "distributions" option is present, the .deb file will be placed in <output-dir>/dist/<distribution>
    directory.

    If multiple "distributions" is specified, multiple .deb files will created in multiple output dirs:
    <output-dir>/dist/<distribution1>, <output-dir>/dist/<distribution2>, etc.
    """
    try:
        with open(package_description) as file:
            parser = metapackage.PackageConfigParser()
            config = parser.parse(file)
        metapackage.create_metapackage(output_dir, workspace, force, config)
    except Exception as e:
        logger.exception(str(e))
        exit(1)
