from zaf.commands.command import CommandId
from zaf.config.options import ConfigOptionId


def run_command(a):
    pass


COMMAND = CommandId(
    'command',
    '',
    callable=run_command,
    config_options=[],
)

COMMAND2 = CommandId(
    'command2',
    '',
    callable=run_command,
    config_options=[],
)

FRAMEWORK_OPTION_1 = ConfigOptionId(
    'b',
    '',
    namespace='a',
    short_alias=True,
)

FRAMEWORK_OPTION_2 = ConfigOptionId(
    'a.b',
    '',
)

COMMAND_OPTION_1 = ConfigOptionId(
    'a',
    '',
    short_name='s',
)

COMMAND_OPTION_2 = ConfigOptionId(
    'b',
    '',
    short_name='s',
)

COMMAND_OPTION_3 = ConfigOptionId(
    'c',
    '',
    short_name='s',
)
