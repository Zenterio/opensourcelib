from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension

from k2.cmd.run import RUN_COMMAND

from . import DO_NOT_USE_OPTION, OPT_OPTION_1, OPT_OPTION_2


@CommandExtension(
    name='withoptionalconfigoptions',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(OPT_OPTION_1, required=False),
        ConfigOption(OPT_OPTION_2, required=False)
    ])
class OptionalOptionsPlugin(AbstractExtension):

    def __init__(self, config, instances):
        try:
            config.get(DO_NOT_USE_OPTION)
        except KeyError:
            pass
        else:
            raise AssertionError('Expected a KeyError to be raised')

    def destroy(self):
        pass
