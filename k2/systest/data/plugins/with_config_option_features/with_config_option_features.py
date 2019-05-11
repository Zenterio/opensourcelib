from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension

from k2.cmd.run import RUN_COMMAND

from . import DEFAULT_OPTION, MULTIPLE_OPTION, TRANSFORM_CHOICE_OPTION, TRANSFORM_OPTION


@CommandExtension(
    name='withconfigoptionfeatures',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(DEFAULT_OPTION, required=False),
        ConfigOption(MULTIPLE_OPTION, required=False),
        ConfigOption(TRANSFORM_CHOICE_OPTION, required=False),
        ConfigOption(TRANSFORM_OPTION, required=False),
    ])
class ConfigOptionFeatures(AbstractExtension):

    def __init__(self, config, instances):
        for key, value in {
                DEFAULT_OPTION: config.get(DEFAULT_OPTION),
                MULTIPLE_OPTION: config.get(MULTIPLE_OPTION),
                TRANSFORM_CHOICE_OPTION: config.get(TRANSFORM_CHOICE_OPTION),
                TRANSFORM_OPTION: config.get(TRANSFORM_OPTION),
        }.items():
            print('{name}: {value}'.format(name=key.name, value=value))

    def destroy(self):
        pass
