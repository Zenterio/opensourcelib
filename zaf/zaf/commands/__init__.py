from zaf.config.options import ConfigOptionId
from zaf.config.types import ConfigChoice, Flag

COMMANDS = ConfigOptionId(
    'commands',
    'List of all commands',
    multiple=True,
    entity=True,
)

COMMAND = ConfigOptionId('internal.command', 'The command to execute')

TARGET_COMMAND = ConfigOptionId(
    'command',
    'The command to analyze',
    option_type=ConfigChoice(COMMANDS),
    namespace='target',
    short_alias=True)

JSON_OUTPUT = ConfigOptionId('json', 'Convert output to json', option_type=Flag())
