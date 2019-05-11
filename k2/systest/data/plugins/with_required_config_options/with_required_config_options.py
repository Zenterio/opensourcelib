from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension

from k2.cmd.run import RUN_COMMAND

from . import REQ_OPTION_1, REQ_OPTION_2


@CommandExtension(
    name='withrequiredconfigoptions',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(REQ_OPTION_1, required=True),
        ConfigOption(REQ_OPTION_2, required=True)
    ])
class RequiredOptionsPlugin(AbstractExtension):

    def __init__(self, config, instances):
        assert config.get(REQ_OPTION_1, None) is not None
        assert config.get(REQ_OPTION_2, None) is not None

    def destroy(self):
        pass
