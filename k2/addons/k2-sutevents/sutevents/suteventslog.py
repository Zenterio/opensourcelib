"""
SUT :abbr:`SUT (Sustem Under Test)` events are used to signal significant events that happen to the SUT.

The SUT-related events used by this extension(s) are:

* :ref:`message-SUT_RESET_STARTED`
* :ref:`message-SUT_RESET_DONE`
* :ref:`message-SUT_RESET_EXPECTED`
* :ref:`message-SUT_RESET_NOT_EXPECTED`

:ref:`message-SUT_RESET_EXPECTED` should be triggered if an imminent reset is
expected (intentional). :ref:`message-SUT_RESET_NOT_EXPECTED` should close the window when
the reset is no longer expected.
:ref:`expect_reset() <method-sutevents.components.SutEvents.expect_reset>` can assist with that.

The data on :ref:`message-SUT_RESET_STARTED` and :ref:`message-SUT_RESET_DONE` is
a boolean signaling if the reset was expected or not.

This extension also provides the additional message IS_SUT_RESET_EXPECTED that can
be used to check if a sut reset is expected at the moment.

See the different classes for additional details.
"""

import logging
import re
from functools import partial

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher, sequential_dispatcher
from zaf.messages.dispatchers import SequentialDispatcher

from k2.cmd.run import RUN_COMMAND, UNINITIALIZE_SUT
from k2.sut import SUT, SUT_RESET_DONE, SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED, \
    SUT_RESET_STARTED
from k2.sut.log import SUT_LOG_SOURCES
from k2.utils.threading import LockableDict, ResetableTimer
from sutevents import IS_SUT_RESET_EXPECTED

from . import LOG_LINE_RECEIVED, SUT_RESET_DONE_DELAY, SUT_RESET_DONE_PATTERN, \
    SUT_RESET_STARTED_PATTERN, SUTEVENTSLOG_ENDPOINT
from .components import SutEvents  # noqa

logger = logging.getLogger(get_logger_name('k2', 'sutevents.log'))

CONFIG_ID_TO_EVENT = {
    SUT_RESET_STARTED_PATTERN: SUT_RESET_STARTED,
    SUT_RESET_DONE_PATTERN: SUT_RESET_DONE
}

EVENT_TO_DELAY_CONFIG_ID = {SUT_RESET_DONE: SUT_RESET_DONE_DELAY}


@CommandExtension(
    name='sutevents',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(SUT_RESET_STARTED_PATTERN, required=False),
        ConfigOption(SUT_RESET_DONE_PATTERN, required=False),
        ConfigOption(SUT_RESET_DONE_DELAY, required=False),
        ConfigOption(SUT_LOG_SOURCES, required=False),
    ],
    endpoints_and_messages={
        SUTEVENTSLOG_ENDPOINT: [
            IS_SUT_RESET_EXPECTED,
            SUT_RESET_STARTED,
            SUT_RESET_DONE,
            SUT_RESET_EXPECTED,
            SUT_RESET_NOT_EXPECTED,
            UNINITIALIZE_SUT,
        ]
    },
    activate_on=[SUT_LOG_SOURCES, SUT_RESET_STARTED_PATTERN, SUT_RESET_DONE_PATTERN])
class SutEventsLogExtension(AbstractExtension):
    """
    Interprets log lines and translates to meaningful sut events.

    This extension listen to log line messages from :ref:`extension-zserial`
    and looks for lines that matches configured events.
    When a line matches an event a message is triggered on the messagebus.

    The log-line patterns to match against is set via configuration:

    * :ref:`option-suts.<ids>.resetstarted.pattern`
    * :ref:`option-suts.<ids>.resetdone.pattern`

    In addition to matching against log-lines, a time-based delay can be set
    to further delay the triggering of the :ref:`message-sut_reset_done` message.
    The delay (in seconds) is specified using :ref:`option-suts.<ids>.resetdone.delay`.
    """

    def __init__(self, config, instances):
        self._entity = instances.get(SUT)
        self._log_sources = config.get(SUT_LOG_SOURCES, entity=self._entity)
        self.pattern_handlers = LockableDict()
        for config_id, event in CONFIG_ID_TO_EVENT.items():
            pattern = config.get(config_id)
            delay = 0
            if pattern:
                delay_config_id = EVENT_TO_DELAY_CONFIG_ID.get(event, None)
                delay = config.get(delay_config_id, 0) if delay_config_id is not None else 0
                self.pattern_handlers[pattern] = ResetableTimer(
                    delay, partial(self._trigger_event, event=event))
        self.sut_reset_expected = False

    def destroy(self):
        self.cancel_triggers()

    def register_dispatchers(self, messagebus):
        if self._log_sources:
            self.dispatcher = SequentialDispatcher(messagebus, self.handle_messages)
            self.dispatcher.register([LOG_LINE_RECEIVED], entities=self._log_sources)

    @callback_dispatcher([UNINITIALIZE_SUT], entity_option_id=SUT)
    def cancel_triggers(self, message=None):
        with self.pattern_handlers.lock:
            for _, trigger in self.pattern_handlers.items():
                trigger.cancel()

    @sequential_dispatcher([SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED], entity_option_id=SUT)
    @requires(messagebus='MessageBus')
    def handle_messages(self, message, messagebus):
        """
        Syncronized message handling.

        A sequential dispatcher with a single handler for multiple events is used
        to ensure that these messages are handled in-order - because the order matters.
        """
        if message.message_id == SUT_RESET_EXPECTED:
            self.sut_reset_expected = True
        elif message.message_id == SUT_RESET_NOT_EXPECTED:
            self.sut_reset_expected = False
        elif message.message_id == LOG_LINE_RECEIVED:
            self.handle_line(message.data, messagebus)

    @callback_dispatcher([IS_SUT_RESET_EXPECTED], [SUTEVENTSLOG_ENDPOINT], entity_option_id=SUT)
    def handle_requests(self, message):
        if message.message_id == IS_SUT_RESET_EXPECTED:
            return self.sut_reset_expected

    def handle_line(self, log_line, messagebus):
        """
        Match log lines according to rules and triggers events.

        :param log_line: the log line
        :param messagebus: the messagebus
        """
        with self.pattern_handlers.lock:
            for pattern, trigger in self.pattern_handlers.items():
                if re.search(pattern, log_line):
                    logger.debug('triggered on line: {line}'.format(line=log_line))
                    self.cancel_triggers()
                    trigger.start(args=[messagebus])
                    break

    def _trigger_event(self, messagebus, event):
        logger.debug('Event {event} being triggered now'.format(event=event.name))
        messagebus.trigger_event(
            event, SUTEVENTSLOG_ENDPOINT, self._entity, data=self.sut_reset_expected)
