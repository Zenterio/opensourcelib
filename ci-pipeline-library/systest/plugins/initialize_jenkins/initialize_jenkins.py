import logging

from k2.cmd.run import INITIALIZE_SUT, RUN_COMMAND
from k2.sut import SUT
from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

logger = logging.getLogger(get_logger_name('k2', 'initializejenkins'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='initializejenkins',
    extends=[RUN_COMMAND],
    config_options=[ConfigOption(SUT, required=True, instantiate_on=True)])
class InitializeJenkins(AbstractExtension):

    def __init__(self, config, instances):
        logger.info('Intializing Jenkins')

    @callback_dispatcher([INITIALIZE_SUT], entity_option_id=SUT)
    @requires(jenkins='Jenkins')
    def initialize_jenkins(self, message, jenkins):
        logger.info('Jenkins initialization complete')
