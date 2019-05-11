from systest.data.plugins.duplicated_options import COMMAND, COMMAND2, COMMAND_OPTION_1, \
    COMMAND_OPTION_2, COMMAND_OPTION_3, FRAMEWORK_OPTION_1, FRAMEWORK_OPTION_2
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, FrameworkExtension


@FrameworkExtension(
    name='duplicatedcommands',
    commands=[COMMAND, COMMAND2],
)
class ProvidesCommands(AbstractExtension):

    def __init__(self, config, instances):
        pass


@FrameworkExtension(
    name='duplicatedframework1', config_options=[ConfigOption(FRAMEWORK_OPTION_1, required=False)])
class Framework1(AbstractExtension):

    def __init__(self, config, instances):
        pass


@FrameworkExtension(
    name='duplicatedframework2', config_options=[ConfigOption(FRAMEWORK_OPTION_2, required=False)])
class Framework2(AbstractExtension):

    def __init__(self, config, instances):
        pass


@CommandExtension(
    name='duplicatedcommand1',
    extends=[COMMAND],
    config_options=[ConfigOption(COMMAND_OPTION_1, required=False)])
class Command1(AbstractExtension):

    def __init__(self, config, instances):
        pass


@CommandExtension(
    name='duplicatedcommand2',
    extends=[COMMAND2],
    config_options=[ConfigOption(COMMAND_OPTION_2, required=False)])
class Command2(AbstractExtension):

    def __init__(self, config, instances):
        pass


@CommandExtension(
    name='duplicatedcommand3',
    extends=[COMMAND],
    config_options=[ConfigOption(COMMAND_OPTION_3, required=False)])
class Command3(AbstractExtension):

    def __init__(self, config, instances):
        pass
