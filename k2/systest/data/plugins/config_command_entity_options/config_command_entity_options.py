from zaf.builtin.config.config import CONFIG_COMMAND
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, CommandExtension, FrameworkExtension

MAIN_ENTITY = ConfigOptionId('entities', '', entity=True, multiple=True, namespace='main')
REQUIRED_MAIN = ConfigOptionId('required', '', at=MAIN_ENTITY)

COMMAND_ENTITY = ConfigOptionId('entities', '', entity=True, multiple=True, namespace='command')
REQUIRED_COMMAND = ConfigOptionId('required', '', at=COMMAND_ENTITY)


@FrameworkExtension(
    name='configcommandentityoptions',
    config_options=[
        ConfigOption(MAIN_ENTITY, required=False),
        ConfigOption(REQUIRED_MAIN, required=True),
    ])
class MainEntityOptions(AbstractExtension):
    pass


@CommandExtension(
    name='configcommandentityoptions',
    extends=[CONFIG_COMMAND],
    config_options=[
        ConfigOption(COMMAND_ENTITY, required=False),
        ConfigOption(REQUIRED_COMMAND, required=True),
    ])
class CommandEntityOptions(AbstractExtension):
    pass
