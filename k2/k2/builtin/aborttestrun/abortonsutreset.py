import logging

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2 import CRITICAL_ABORT
from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT_RESET_STARTED

from . import ABORT_ON_UNEXPECTED_SUT_RESET, ABORT_ON_UNEXPECTED_SUT_RESET_ENDPOINT

logger = logging.getLogger(get_logger_name('k2', 'aborttestrun'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='aborttestrun',
    extends=[RUN_COMMAND],
    config_options=[ConfigOption(ABORT_ON_UNEXPECTED_SUT_RESET, required=True)],
    endpoints_and_messages={ABORT_ON_UNEXPECTED_SUT_RESET_ENDPOINT: [CRITICAL_ABORT]},
    activate_on=[ABORT_ON_UNEXPECTED_SUT_RESET])
class AbortOnUnexpectedSutReset(AbstractExtension):
    """
    Aborts test run on unexpected sut reset.

    This listens to the message SUT_RESET_STARTED and if the the sut reset is unexpected
    a CRITICAL_ABORT is sent that will immediately stop the test run.
    """

    def __init__(self, config, instances):
        pass

    @callback_dispatcher([SUT_RESET_STARTED])
    @requires(messagebus='MessageBus')
    def handle_sut_reset_started(self, message, messagebus):
        if not message.data:
            messagebus.trigger_event(CRITICAL_ABORT, ABORT_ON_UNEXPECTED_SUT_RESET_ENDPOINT)
