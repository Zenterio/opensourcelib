import click

import debpacker
from debpacker.common.loghandling import configure_logging
from debpacker.ui import metapackage, toolchain


@click.group()
@click.version_option(debpacker.__version__)
@click.option('--verbose', '-v', default=False, is_flag=True, help='Activate verbose output')
def entry_point(verbose):
    configure_logging(verbose)


entry_point.add_command(toolchain.package_toolchain)
entry_point.add_command(toolchain.package_toolchain_list)
entry_point.add_command(metapackage.create_metapackage)

if __name__ == '__main__':
    entry_point()
