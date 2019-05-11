"""
Utilities for managing addons.

==================
The create command
==================

Intended to simplify creation of new addons, the create command generates the
basic structure required for a K2 addon. The create command is based on a
command line wizard. The wizard will ask question about the addon to be created
and when completed, it will write the addon structure to disk.

To launch the wizard and start creating a new addon, run:

    zk2 addon create

After creating a new addon, the local Python virtual environment must be
refreshed to include the new addon, by running:

    make venv

To include the new addon in the K2 package, make sure to add it to the
requirements.txt file in the K2 root directory.
"""

import logging
import os

from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Choice
from zaf.extensions.extension import FrameworkExtension, get_logger_name

from .generator import generate_command_extension_entrypoint, \
    generate_framework_extension_entrypoint, generate_initial_unittest, generate_setup_py_file
from .wizard import run_command_extension_wizard, run_generic_addon_wizard

logger = logging.getLogger(get_logger_name('k2', 'addon'))


def addon(core):
    """Utilities for managing addons."""
    subcommand = core.config.get(ADDON_SUBCOMMAND)
    try:
        if subcommand == 'create':
            _create_addon_using_wizard(core)
            logger.info('Addon created successfully')
            return 0
    except Exception as e:
        msg = 'Could not create addon: {msg}'.format(msg=str(e))
        logger.debug(msg, exc_info=True)
        logger.error(msg)
    return 1


def _create_addon_using_wizard(core):
    addon_info = run_generic_addon_wizard()
    if addon_info is not None:
        if addon_info.addon_type == 'command':
            addon_info = _merge_namespaces(addon_info, run_command_extension_wizard(core))
        _make_default_addon_layout(addon_info)


def _make_default_addon_layout(addon_info):
    root_directory = addon_info.addon_path
    package = addon_info.package_name
    package_home = os.path.join(root_directory, package, package)

    _make_directories(os.path.join(package_home, 'test'))
    _make_file(
        os.path.join(root_directory, package, 'setup.py'),
        contents=generate_setup_py_file(addon_info))
    _make_file(os.path.join(package_home, '__init__.py'), contents='')
    _make_file(os.path.join(package_home, 'test', '__init__.py'), contents='')
    if addon_info.addon_type == 'command':
        entrypoint_contents = generate_command_extension_entrypoint(addon_info)
    else:
        entrypoint_contents = generate_framework_extension_entrypoint(addon_info)
    _make_file(
        os.path.join(package_home, addon_info.package_name + '.py'), contents=entrypoint_contents)
    _make_file(
        os.path.join(package_home, 'test', 'test_' + addon_info.package_name + '.py'),
        contents=generate_initial_unittest(addon_info))


def _merge_namespaces(*namespaces):
    from pypsi.namespace import Namespace

    merged_namespace = Namespace()
    for namespace in namespaces:
        for k, v in namespace.__dict__.items():
            if k in merged_namespace:
                raise ValueError('Duplicate key in Namespace: {key}'.format(key=k))
        merged_namespace.__dict__.update(namespace.__dict__)
    return merged_namespace


def _make_directories(path):
    logger.info('Creating directories: {path}'.format(path=path))
    os.makedirs(path)


def _make_file(path, contents):
    logger.info('Writing file: {path}'.format(path=path))
    with open(path, 'w') as f:
        f.write(contents)


ADDON_SUBCOMMAND = ConfigOptionId(
    'addon.subcommand', 'The subcommand to addon', option_type=Choice(['create']), argument=True)

ADDON_COMMAND = CommandId(
    'addon', addon.__doc__, addon, config_options=[
        ConfigOption(ADDON_SUBCOMMAND, required=True),
    ])


@FrameworkExtension(
    'addon',
    commands=[ADDON_COMMAND],
    groups=['addon'],
)
class AddonExtension(object):
    """Provides the addon command."""

    def __init__(self, config, instances):
        pass
