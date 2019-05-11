from zaf.application import BEFORE_COMMAND
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import FrameworkExtension
from zaf.messages.decorator import callback_dispatcher

ACTIVATE_ON = ConfigOptionId('activate.on', 'Activate when this is true', bool, default=False)


@FrameworkExtension(
    name='extensionthatcanbeactivated',
    config_options=[ConfigOption(ACTIVATE_ON, required=False)],
    activate_on=[ACTIVATE_ON],
)
class ExtensionThatCanBeActivated(object):

    def __init__(self, config, instances):
        pass

    @callback_dispatcher([BEFORE_COMMAND])
    def my_dispatcher(self, message):
        print('extension was activated')
