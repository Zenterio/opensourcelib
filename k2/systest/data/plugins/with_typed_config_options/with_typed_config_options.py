from zaf.config.options import ConfigOption
from zaf.extensions.extension import CommandExtension

from k2.cmd.run import RUN_COMMAND

from . import BOOL_OPTION, CHOICE_OPTION, FLOAT_OPTION, INT_OPTION, PATH_OPTION, STR_OPTION


@CommandExtension(
    name='withtypedconfigoptions',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(STR_OPTION, required=False),
        ConfigOption(INT_OPTION, required=False),
        ConfigOption(FLOAT_OPTION, required=False),
        ConfigOption(CHOICE_OPTION, required=False),
        ConfigOption(PATH_OPTION, required=False),
        ConfigOption(BOOL_OPTION, required=False)
    ])
class TypedOptionsPlugin():

    def __init__(self, config, instances):
        pass
