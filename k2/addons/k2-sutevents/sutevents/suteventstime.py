import logging

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher, sequential_dispatcher

from k2.cmd.run import RUN_COMMAND, UNINITIALIZE_SUT
from k2.sut import SUT, SUT_RESET_DONE, SUT_RESET_DONE_TIMEOUT, SUT_RESET_EXPECTED, \
    SUT_RESET_NOT_EXPECTED, SUT_RESET_STARTED
from k2.utils.threading import ResetableTimer
from sutevents import IS_SUT_RESET_EXPECTED
from zserial import SERIAL_ENABLED

from . import SUT_RESET_DONE_PATTERN, SUT_RESET_STARTED_PATTERN, SUTEVENTSTIME_ENDPOINT
from .components import SutEvents  # noqa

logger = logging.getLogger(get_logger_name('k2', 'sutevents.time'))


@CommandExtension(
    name='sutevents',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(SUT_RESET_DONE_TIMEOUT, required=True),
        ConfigOption(SERIAL_ENABLED, required=False),
        ConfigOption(SUT_RESET_STARTED_PATTERN, required=False),
        ConfigOption(SUT_RESET_DONE_PATTERN, required=False),
    ],
    endpoints_and_messages={
        SUTEVENTSTIME_ENDPOINT: [
            IS_SUT_RESET_EXPECTED,
            SUT_RESET_STARTED,
            SUT_RESET_DONE,
            SUT_RESET_EXPECTED,
            SUT_RESET_NOT_EXPECTED,
        ]
    },
    deactivate_on=[SERIAL_ENABLED, SUT_RESET_STARTED_PATTERN, SUT_RESET_DONE_PATTERN])
class SutEventsTimeExtension(AbstractExtension):
    """
    A time-based implementation that should only be used if logs are not available.

    It sends :ref:`message-SUT_RESET_STARTED` on :ref:`message-SUT_RESET_EXPECTED`, and
    :ref:`message-SUT_RESET_DONE` using a timer
    (configured with :ref:`option-suts.<ids>.resetdone.timeout`),
    instead of by parsing log-lines.
    """

    def __init__(self, config, instances):
        self._entity = instances.get(SUT)
        sut_reset_done_delay = max(0, config.get(SUT_RESET_DONE_TIMEOUT) - 10)
        self._timer = ResetableTimer(sut_reset_done_delay, self.reset_stopped_identified)
        self.sut_reset_expected = False

    @sequential_dispatcher([SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED], entity_option_id=SUT)
    @requires(messagebus='MessageBus')
    def message_handler(self, message, messagebus):
        logger.debug('Handling message {name}'.format(name=message.message_id.name))
        if message.message_id == SUT_RESET_EXPECTED:
            self.sut_reset_expected = True
            self.reset_started_identified(messagebus)
        elif message.message_id == SUT_RESET_NOT_EXPECTED:
            self.sut_reset_expected = False
        elif message.message_id == IS_SUT_RESET_EXPECTED:
            return self.sut_reset_expected

    @callback_dispatcher([IS_SUT_RESET_EXPECTED], [SUTEVENTSTIME_ENDPOINT], entity_option_id=SUT)
    def handle_requests(self, message):
        if message.message_id == IS_SUT_RESET_EXPECTED:
            return self.sut_reset_expected

    @callback_dispatcher([UNINITIALIZE_SUT], entity_option_id=SUT)
    def handle_uninitialize_sut(self, message):
        logger.debug('Unitilize SUT, canceling timer')
        self._timer.cancel()

    def reset_started_identified(self, messagebus):
        logger.info('Reset started detected for sut {entity}'.format(entity=self._entity))
        messagebus.trigger_event(
            SUT_RESET_STARTED, SUTEVENTSTIME_ENDPOINT, self._entity, data=self.sut_reset_expected)

        logger.info(
            'Waiting {seconds} seconds for sut {entity} to have restarted'.format(
                entity=self._entity, seconds=self._timer.interval))
        self._timer.start(args=[messagebus])

    def reset_stopped_identified(self, messagebus):
        logger.info('Reset completed detected for sut {entity}'.format(entity=self._entity))
        messagebus.trigger_event(
            SUT_RESET_DONE, SUTEVENTSTIME_ENDPOINT, self._entity, data=self.sut_reset_expected)
