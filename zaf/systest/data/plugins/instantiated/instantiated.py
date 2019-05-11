from zaf.builtin.extensions import EXTENSIONS_COMMAND
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension

from . import DEPENDENT_OPTION, INSTANCES


@CommandExtension(
    name='instantiated',
    extends=[EXTENSIONS_COMMAND],
    config_options=[
        ConfigOption(INSTANCES, required=True, instantiate_on=True),
        ConfigOption(DEPENDENT_OPTION, required=True),
    ])
class InstantiatedExtension(AbstractExtension):

    def __init__(self, config, instances):
        for key, value in {
                INSTANCES: config.get(INSTANCES),
                DEPENDENT_OPTION: config.get(DEPENDENT_OPTION),
        }.items():
            print(
                '{instance}: {key}: {value}'.format(
                    instance=instances[INSTANCES], key=key.name, value=value))

    def destroy(self):
        pass
