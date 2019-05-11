"""Provides the *config* command that shows the loaded config."""
from zaf.application import ApplicationContext
from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import FrameworkExtension


def print_configuration(core):
    """
    Show the available config.

    Example to show all config::

        zaf config

    Example to show a specific config option::

        zaf config config.option.name
    """
    core.config.print_config(core.config.get(CONFIG_OPTION_NAME))
    return 0


CONFIG_OPTION_NAME = ConfigOptionId(
    'option.name',
    'Name of the config option to print.',
    multiple=True,
    argument=True,
    namespace='config',
    short_alias=True)

CONFIG_COMMAND = CommandId(
    'config',
    print_configuration.__doc__,
    print_configuration,
    config_options=[ConfigOption(CONFIG_OPTION_NAME, required=False)],
    hidden=True,
    application_contexts=ApplicationContext.EXTENDABLE)


@FrameworkExtension('configcommand', commands=[CONFIG_COMMAND], groups=['config'])
class ConfigCommand(object):
    """Provides the config command."""

    def __init__(self, config, instances):
        pass
