from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, FrameworkExtension

COMMAND_OPTION = ConfigOptionId('command.option', 'option on command')
SUBCOMMAND_OPTION = ConfigOptionId('subcommand.option', 'option on subcommand')
SUBSUBCOMMAND_OPTION = ConfigOptionId('subsubcommand.option', 'option on subsubcommand')


def command(application):
    cfg = application.config
    print('command', cfg.get(COMMAND_OPTION))


def subcommand(application):
    cfg = application.config
    print('subcommand', cfg.get(COMMAND_OPTION), cfg.get(SUBCOMMAND_OPTION))


def subsubcommand(application):
    cfg = application.config
    print(
        'subsubcommand', cfg.get(COMMAND_OPTION), cfg.get(SUBCOMMAND_OPTION),
        cfg.get(SUBSUBCOMMAND_OPTION))


COMMAND = CommandId(
    'command', 'description', command, [ConfigOption(COMMAND_OPTION, required=True)])
SUBCOMMAND = CommandId(
    'subcommand',
    'description',
    subcommand, [ConfigOption(SUBCOMMAND_OPTION, required=True)],
    parent=COMMAND)
SUBSUBCOMMAND = CommandId(
    'subsubcommand',
    'description',
    subsubcommand, [ConfigOption(SUBSUBCOMMAND_OPTION, required=True)],
    parent=SUBCOMMAND)


@FrameworkExtension('subcommands', commands=[COMMAND, SUBCOMMAND, SUBSUBCOMMAND])
class Commands(AbstractExtension):
    pass
